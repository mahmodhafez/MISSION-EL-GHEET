import os
os.environ["HF_HUB_OFFLINE"]="1"
os.environ["TRANSFORMERS_OFFLINE"]="1"
from pathlib import Path
import datetime as dt
import hashlib
import json
import time
import numpy as np
import pandas as pd
import torch
from chronos import Chronos2Pipeline

root=Path(__file__).resolve().parent
torch.set_num_threads(4)
candidates=[]
for name in ["smoke20_verified","adaptation200"]:
    r=json.loads((root/name/"results.json").read_text())
    assert r["status"]=="completed",name+" did not complete"
    candidates.append((r["fine_tuned"]["scores"]["et0_mm_day"]["mae"],name))
selected=min(candidates)[1]
df=pd.concat([pd.read_csv(root.parent/"weather_et0.csv",parse_dates=["date"]),pd.read_csv(root.parent/"weather_et0_2026_Jan_Oct.csv",parse_dates=["date"])],ignore_index=True)
dates=pd.DatetimeIndex(df.date)
assert dates.is_unique and dates.is_monotonic_increasing
values=df[["tmax_c","et0_mm_day"]].to_numpy(dtype=np.float32).T
trainmask=dates<=pd.Timestamp("2018-12-31")
train=values[:,trainmask]
phase=np.array([dt.date(2000,d.month,d.day).timetuple().tm_yday for d in dates[trainmask]])
issues=list(pd.date_range("2026-07-01","2026-10-24",freq="7D"))
contexts=[];truth=[];persistence=[];climatology=[]
for issue in issues:
    ci=dates.get_loc(issue-pd.Timedelta(days=7));ti=dates.get_loc(issue+pd.Timedelta(days=1))
    contexts.append(values[:,ci-59:ci+1].copy());truth.append(values[:,ti:ti+7])
    persistence.append(np.repeat(values[:,ci:ci+1],7,axis=1))
    forecasts=[]
    for day in dates[ti:ti+7]:
        delta=np.abs(phase-dt.date(2000,day.month,day.day).timetuple().tm_yday)
        mask=np.minimum(delta,366-delta)<=15
        forecasts.append(np.quantile(train[:,mask],[.1,.5,.9],axis=1).T)
    climatology.append(np.stack(forecasts,axis=1))
truth=np.stack(truth);climatology=np.stack(climatology);persistence=np.stack(persistence)
def predict(path):
    pipeline=Chronos2Pipeline.from_pretrained(str(path),device_map="cuda",dtype=torch.float32,local_files_only=True)
    pipeline.model.eval();torch.cuda.synchronize();start=time.perf_counter()
    q,_=pipeline.predict_quantiles(contexts,prediction_length=14,context_length=60,batch_size=4,cross_learning=False,quantile_levels=[.1,.5,.9])
    torch.cuda.synchronize();elapsed=time.perf_counter()-start
    array=np.stack([x.cpu().float().numpy()[:,7:14,:] for x in q])
    del pipeline;torch.cuda.empty_cache()
    return array,elapsed
def metrics(array):
    results={}
    for i,name in enumerate(["tmax_c","et0_mm_day"]):
        error=array[:,i,:,1]-truth[:,i,:]
        residual=truth[:,i,:,None]-array[:,i,:,:]
        levels=np.array([.1,.5,.9])
        results[name]={"mae":float(np.mean(abs(error))),"rmse":float(np.sqrt(np.mean(error**2))),"bias":float(np.mean(error)),
                       "mae_by_lead_1_to_7":np.mean(abs(error),axis=0).tolist(),
                       "interval_80_coverage":float(np.mean((truth[:,i,:]>=array[:,i,:,0])&(truth[:,i,:]<=array[:,i,:,2]))),
                       "mean_interval_width":float(np.mean(array[:,i,:,2]-array[:,i,:,0])),
                       "mean_pinball_loss":float(np.mean(np.maximum(levels*residual,(levels-1)*residual)))}
    return results
zero,zero_seconds=predict(root/"checkpoint")
tuned,tuned_seconds=predict(root/selected/"training/finetuned-ckpt")
report={"selected_adapter":selected,"selection_validation_et0_mae":dict((name,float(score)) for score,name in candidates),
        "checkpoint_revision_date":"2026-06-05","issue_dates":[str(d.date()) for d in issues],"nonoverlapping_weeks":len(issues),
        "forecast_days_per_target":len(issues)*7,"forecast_contract":"Cutoff D-7; 14 steps; score steps8-14 for D+1..D+7",
        "scores":{"zero_shot":metrics(zero),"fine_tuned":metrics(tuned),"seasonal_climatology":metrics(climatology),
                  "persistence":{name:{"mae":float(np.mean(abs(persistence[:,i,:]-truth[:,i,:])))} for i,name in enumerate(["tmax_c","et0_mm_day"])}},
        "prediction_seconds":{"zero_shot":zero_seconds,"fine_tuned":tuned_seconds},
        "limits":["17 July-October weekly origins at one provisional point", "Current revised POWER archive with simulated latency, not prospective real-time evaluation", "Target ET0 is calculated from gridded products, not independent field observations", "No agricultural decision or farmer outcome validated"]}
rng=np.random.default_rng(20261111)
bootstrap=rng.integers(0,len(issues),size=(2000,len(issues)))
comparisons={}
for base_name,base in [("zero_shot",zero),("seasonal_climatology",climatology)]:
    for i,name in enumerate(["tmax_c","et0_mm_day"]):
        improvement=np.mean(abs(base[:,i,:,1]-truth[:,i,:]),axis=1)-np.mean(abs(tuned[:,i,:,1]-truth[:,i,:]),axis=1)
        samples=improvement[bootstrap].mean(axis=1)
        comparisons[base_name+"_vs_tuned_"+name]={"mean_mae_reduction_positive_is_better":float(improvement.mean()),"descriptive_week_bootstrap_95_interval":np.quantile(samples,[.025,.975]).tolist()}
report["paired_diagnostics"]=comparisons
report["input_hashes"]={name:hashlib.sha256((root.parent/name).read_bytes()).hexdigest() for name in ["weather_et0.csv","weather_et0_2026_Jan_Oct.csv"]}
(root/"holdout_results.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
np.savez_compressed(root/"holdout_predictions.npz",truth=truth,zero_shot=zero,fine_tuned=tuned,climatology=climatology,persistence=persistence)
print(json.dumps(report,indent=2))
