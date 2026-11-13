import os
os.environ["HF_HUB_OFFLINE"]="1"
os.environ["TRANSFORMERS_OFFLINE"]="1"
import json
from pathlib import Path
import torch
import pandas as pd
from chronos import Chronos2Pipeline
from accelerate.utils import extract_model_from_parallel
from transformers import set_seed

root=Path(__file__).resolve().parent
set_seed(20261111);torch.set_num_threads(4)
df=pd.read_csv(root.parent/"weather_et0.csv")
train=df.loc[df.date<="2018-12-31",["tmax_c","et0_mm_day"]].to_numpy(dtype="float32").T
context=train[:,-60:]
base=Chronos2Pipeline.from_pretrained(str(root/"checkpoint"),device_map="cuda",dtype=torch.float32,local_files_only=True)
adapted=base.fit([train],prediction_length=14,context_length=60,finetune_mode="lora",learning_rate=1e-5,
                 num_steps=1,batch_size=4,min_past=60,output_dir=root/"reload_diagnosis",disable_tqdm=True,report_to="none")
def predict(p):return p.predict_quantiles([context],prediction_length=14,context_length=60,batch_size=4,cross_learning=False,quantile_levels=[.1,.5,.9])[0][0].detach().cpu()
report={"training_flag_after_fit":adapted.model.training,"original_forward_hook":hasattr(adapted.model,"_original_forward"),"forward_type":str(type(adapted.model.forward))}
a=predict(adapted);repeat=predict(adapted)
report["repeat_difference"]=float((a-repeat).abs().max())
adapted.model.eval()
b=predict(adapted)
report["eval_only_difference"]=float((a-b).abs().max())
adapted.model=extract_model_from_parallel(adapted.model,keep_fp32_wrapper=False)
c=predict(adapted)
report["remove_mixed_precision_hook_difference"]=float((b-c).abs().max())
reloaded=Chronos2Pipeline.from_pretrained(str(root/"reload_diagnosis/finetuned-ckpt"),device_map="cuda",dtype=torch.float32,local_files_only=True)
d=predict(reloaded)
report["raw_vs_reload_difference"]=float((a-d).abs().max())
report["unwrapped_vs_reload_difference"]=float((c-d).abs().max())
report["reloaded_training_flag"]=reloaded.model.training
(root/"reload_diagnosis/result.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
print(json.dumps(report,indent=2))
