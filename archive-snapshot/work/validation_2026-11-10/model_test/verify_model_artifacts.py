"""Independent saved-artifact checks; no new model fitting or inference."""
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd

root=Path(__file__).resolve().parent
report=json.loads((root/"holdout_results.json").read_text())
arrays=np.load(root/"holdout_predictions.npz")
df=pd.concat([pd.read_csv(root.parent/"weather_et0.csv",parse_dates=["date"]),pd.read_csv(root.parent/"weather_et0_2026_Jan_Oct.csv",parse_dates=["date"])],ignore_index=True).set_index("date")
checks=[]
for i,issue in enumerate(pd.to_datetime(report["issue_dates"])):
    expected=df.loc[issue+pd.Timedelta(days=1):issue+pd.Timedelta(days=7),["tmax_c","et0_mm_day"]].to_numpy(dtype=np.float32).T
    assert np.array_equal(expected,arrays["truth"][i])
    last=df.loc[issue-pd.Timedelta(days=7),["tmax_c","et0_mm_day"]].to_numpy(dtype=np.float32)
    assert np.array_equal(np.repeat(last[:,None],7,axis=1),arrays["persistence"][i])
checks.extend(["all held-out target dates/values match source CSV","persistence uses issue-date-minus-seven cutoff"])
for method,key in [("zero_shot","zero_shot"),("fine_tuned","fine_tuned"),("seasonal_climatology","climatology")]:
    for k,target in enumerate(["tmax_c","et0_mm_day"]):
        mae=float(np.abs(arrays[key][:,k,:,1].astype(np.float64)-arrays["truth"][:,k,:]).mean())
        assert abs(mae-report["scores"][method][target]["mae"])<2e-6
checks.append("all reported model/climatology MAE values independently reproduced")
for name in ["smoke20_verified","adaptation200"]:
    run=json.loads((root/name/"results.json").read_text())
    assert run["status"]=="completed" and run["reload"]["within_0_001"]
    assert run["lora"]["changed_adapter_tensors"]==run["lora"]["adapter_tensors"]>0
    assert (root/name/"training/finetuned-ckpt/adapter_model.safetensors").is_file()
checks.append("completed runs record real adapter updates and passing reload checks; adapters exist")
for name,expected in report["input_hashes"].items():
    assert hashlib.sha256((root.parent/name).read_bytes()).hexdigest()==expected
checks.append("current data hashes match evaluated data")
result={"status":"passed","checks":checks,"weekly_origins":len(report["issue_dates"]),"days_per_target":arrays["truth"].shape[0]*arrays["truth"].shape[2]}
(root/"artifact_verification.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
print(json.dumps(result,indent=2))
