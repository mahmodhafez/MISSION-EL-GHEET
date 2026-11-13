"""Bounded, local Chronos-2 LoRA feasibility and diagnostic validation test."""
import argparse
import datetime as dt
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import time
import traceback

os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")
os.environ.setdefault("WANDB_DISABLED", "true")
import numpy as np
import pandas as pd
import torch
from chronos import Chronos2Pipeline
from transformers import TrainerCallback, set_seed
from accelerate.utils import extract_model_from_parallel
import peft

parser=argparse.ArgumentParser()
parser.add_argument("--steps",type=int,default=20)
parser.add_argument("--run-id",default="smoke20")
args=parser.parse_args()
root=Path(__file__).resolve().parent
out=root/args.run_id
out.mkdir(exist_ok=True)
report={"run_id":args.run_id,"started_utc":dt.datetime.now(dt.timezone.utc).isoformat(),
        "status":"running","purpose":"Execution feasibility and diagnostic validation, not final agricultural or forecasting validation"}
def save():
    (out/"results.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
def event(label,**kwargs):
    print(json.dumps({"event":label,**kwargs}),flush=True)
def digest(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):h.update(chunk)
    return h.hexdigest()
def forecast(pipeline,inputs):
    pipeline.model.eval()
    torch.cuda.synchronize(); start=time.perf_counter()
    q,_=pipeline.predict_quantiles(inputs,prediction_length=14,context_length=60,
                                  batch_size=4,cross_learning=False,quantile_levels=[.1,.5,.9])
    torch.cuda.synchronize()
    array=np.stack([item.float().cpu().numpy()[:,7:14,:] for item in q])
    return array,time.perf_counter()-start
def score(pred,truth):
    result={}
    for k,name in enumerate(["tmax_c","et0_mm_day"]):
        median=pred[:,k,:,1]
        error=median-truth[:,k,:]
        residual=truth[:,k,:,None]-pred[:,k,:,:]
        levels=np.array([.1,.5,.9])
        result[name]={"mae":float(np.mean(abs(error))),"rmse":float(np.sqrt(np.mean(error**2))),
                      "bias":float(np.mean(error)),"mae_by_lead_1_to_7":np.mean(abs(error),axis=0).tolist(),
                      "interval_80_coverage":float(np.mean((truth[:,k,:]>=pred[:,k,:,0])&(truth[:,k,:]<=pred[:,k,:,2]))),
                      "interval_mean_width":float(np.mean(pred[:,k,:,2]-pred[:,k,:,0])),
                      "mean_pinball_loss":float(np.mean(np.maximum(levels*residual,(levels-1)*residual)))}
    return result

class VerifyLoRA(TrainerCallback):
    def __init__(self):self.initial={}
    def on_train_begin(self,args,state,control,model=None,**kwargs):
        trainable={name:p for name,p in model.named_parameters() if p.requires_grad}
        assert trainable and all("lora_" in name for name in trainable),"Adapter-only training is required"
        self.initial={name:p.detach().cpu().float().clone() for name,p in trainable.items()}
        count=sum(p.numel() for p in trainable.values())
        total=sum(p.numel() for p in model.parameters())
        assert count/total<.05,"Unexpected trainable parameter fraction"
        report["lora"]={"trainable_parameters":count,"total_parameters":total,"fraction":count/total,"adapter_tensors":len(trainable)}
        save();event("lora_verified",**report["lora"])
    def on_train_end(self,args,state,control,model=None,**kwargs):
        changed=0; maxdiff=0.
        for name,p in model.named_parameters():
            if name in self.initial:
                diff=float((p.detach().cpu().float()-self.initial[name]).abs().max())
                changed+=diff>0;maxdiff=max(maxdiff,diff)
        assert changed>0,"No adapter parameter changed"
        report["lora"].update({"changed_adapter_tensors":changed,"max_absolute_parameter_change":maxdiff,"completed_steps":state.global_step})
        save();event("updates_verified",**report["lora"])

try:
    set_seed(20261111)
    torch.set_num_threads(4)
    assert torch.cuda.is_available(),"CUDA is unavailable; no silent CPU training fallback"
    report["versions"]={p:importlib.metadata.version(p) for p in ["torch","chronos-forecasting","peft","transformers","accelerate","numpy","pandas"]}
    report["hardware"]={"gpu":torch.cuda.get_device_name(0),"total_vram_bytes":torch.cuda.get_device_properties(0).total_memory,
                        "free_vram_before_bytes":torch.cuda.mem_get_info()[0]}
    csv=root.parent/"weather_et0.csv"
    report["input_sha256"]=digest(csv)
    report["checkpoint_sha256"]=digest(root/"checkpoint/model.safetensors")
    assert report["checkpoint_sha256"]=="ddcda3c7508bf2528087723e98a20707cc04b7f370ae275a9fd88078ddba4f42"
    df=pd.read_csv(csv,parse_dates=["date"])
    assert df["date"].is_monotonic_increasing and not df["date"].duplicated().any()
    assert (df["date"].diff().dropna()==pd.Timedelta(days=1)).all()
    target=df[["tmax_c","et0_mm_day"]].to_numpy(dtype=np.float32).T
    assert np.isfinite(target).all()
    dates=pd.DatetimeIndex(df["date"])
    trainmask=dates<=pd.Timestamp("2018-12-31")
    train=target[:,trainmask]
    issues=[pd.Timestamp(year=y,month=m,day=15) for y in [2019,2020,2021] for m in range(1,13)]
    inputs=[];truth=[];persistence=[];climatology=[]
    train_dates=dates[trainmask]
    train_phase=np.array([dt.date(2000,d.month,d.day).timetuple().tm_yday for d in train_dates])
    for issue in issues:
        cutoff=issue-pd.Timedelta(days=7)
        ci=dates.get_loc(cutoff)
        inputs.append(target[:,ci-59:ci+1].copy())
        ti=dates.get_loc(issue+pd.Timedelta(days=1))
        truth.append(target[:,ti:ti+7])
        persistence.append(np.repeat(target[:,ci:ci+1],7,axis=1))
        clim=[]
        for day in dates[ti:ti+7]:
            phase=dt.date(2000,day.month,day.day).timetuple().tm_yday
            delta=np.abs(train_phase-phase);mask=np.minimum(delta,366-delta)<=15
            clim.append(np.quantile(train[:,mask],[.1,.5,.9],axis=1).T)
        climatology.append(np.stack(clim,axis=1))
    truth=np.stack(truth);persist=np.stack(persistence);clim=np.stack(climatology)
    report["experiment"]={"training_period":[str(train_dates[0].date()),str(train_dates[-1].date())],
                          "validation_issues":[str(d.date()) for d in issues],"issue_count":len(issues),
                          "targets":["tmax_c","et0_mm_day"],"input_cutoff":"issue date minus 7 days",
                          "model_horizon_steps":14,"scored_steps":[8,9,10,11,12,13,14],"context_days":60,
                          "batch_series":4,"learning_rate":1e-5,"steps":args.steps,"cross_learning":False,
                          "limits":["36 diagnostic validation origins, not an untouched final test","Unknown pretraining overlap","Current archive with simulated latency, not real-time vintages","No crop-outcome or decision benefit evaluated"]}
    report["baseline_scores"]={"seasonal_climatology":score(clim,truth),"persistence":{name:{"mae":float(np.mean(abs(persist[:,i,:]-truth[:,i,:])))} for i,name in enumerate(["tmax_c","et0_mm_day"])}}
    save();event("loading_model",hardware=report["hardware"])
    pipeline=Chronos2Pipeline.from_pretrained(str(root/"checkpoint"),device_map="cuda",dtype=torch.float32,local_files_only=True)
    torch.cuda.reset_peak_memory_stats()
    zero,seconds=forecast(pipeline,inputs)
    report["zero_shot"]={"scores":score(zero,truth),"forecast_seconds":seconds}
    save();event("zero_shot_completed",seconds=seconds,scores=report["zero_shot"]["scores"])
    callback=VerifyLoRA()
    torch.cuda.synchronize();start=time.perf_counter()
    adapted=pipeline.fit([train],prediction_length=14,context_length=60,finetune_mode="lora",learning_rate=1e-5,
                         num_steps=args.steps,batch_size=4,min_past=60,output_dir=out/"training",callbacks=[callback],
                         logging_steps=5,disable_tqdm=True,report_to="none",seed=20261111,data_seed=20261111)
    torch.cuda.synchronize()
    report["training_seconds"]=time.perf_counter()-start
    report["peak_allocated_vram_bytes"]=torch.cuda.max_memory_allocated()
    report["peak_reserved_vram_bytes"]=torch.cuda.max_memory_reserved()
    # Trainer leaves training mode and mixed-precision forward hooks attached.
    # Match the FP32/eval inference contract of a saved/reloaded checkpoint.
    adapted.model=extract_model_from_parallel(adapted.model,keep_fp32_wrapper=False)
    adapted.model.eval()
    tuned,seconds=forecast(adapted,inputs)
    report["fine_tuned"]={"scores":score(tuned,truth),"forecast_seconds":seconds}
    np.savez_compressed(out/"diagnostic_predictions.npz",truth=truth,zero_shot=zero,fine_tuned=tuned,climatology=clim,persistence=persist)
    before_reload,_=forecast(adapted,inputs[:1])
    del adapted,pipeline
    import gc
    gc.collect();torch.cuda.empty_cache()
    reloaded=Chronos2Pipeline.from_pretrained(str(out/"training/finetuned-ckpt"),device_map="cuda",dtype=torch.float32,local_files_only=True)
    after_reload,_=forecast(reloaded,inputs[:1])
    reload_difference=float(np.max(abs(before_reload-after_reload)))
    report["reload"]={"max_prediction_difference":reload_difference,"within_0_001":reload_difference<.001}
    assert reload_difference<.001,"Adapter reload materially changed predictions"
    report["status"]="completed"
    report["finished_utc"]=dt.datetime.now(dt.timezone.utc).isoformat()
    save();event("completed",training_seconds=report["training_seconds"],peak_vram=report["peak_allocated_vram_bytes"],reload=report["reload"],scores=report["fine_tuned"]["scores"])
except Exception as exc:
    report["status"]="failed";report["error"]=repr(exc);report["traceback"]=traceback.format_exc();save()
    event("failed",error=repr(exc));raise
