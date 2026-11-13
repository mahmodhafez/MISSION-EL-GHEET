"""Limited comparison with a published monthly Sakha station table, not calibration."""
import csv
import json
from pathlib import Path
import statistics as st

root=Path(__file__).resolve().parent
with (root/"weather_et0.csv").open(encoding="utf-8") as f:rows=list(csv.DictReader(f))
# Aiad2019, Table2, printedp149. Wind is reported as km/day at2m.
reference={
"2015-11":(24.40,14.42,75.6,70.30),"2015-12":(19.70,8.36,77.9,57.90),
"2016-01":(18.40,6.35,74.05,69.20),"2016-02":(22.58,9.35,69.05,58.80),
"2016-03":(24.50,11.60,69.9,63.20),"2016-04":(30.03,18.62,61.7,87.10),
"2016-05":(30.40,22.80,58.4,97.00),"2016-06":(33.60,26.30,61.15,112.80),
"2016-07":(33.70,26.10,69.75,105.50),"2016-08":(33.60,26.00,70.30,92.80),
"2016-09":(32.60,24.30,67.45,95.10)}
variables=["tmax_c","tmin_c","rh_percent","wind2_m_s"]
comparisons=[]
for month,values in reference.items():
    observed=list(values);observed[3]*=1000/86400
    sample=[r for r in rows if r["date"].startswith(month)]
    comparisons.append({"month":month,"days":len(sample),"differences_power_minus_published":{
        key:st.mean(float(r[key]) for r in sample)-value for key,value in zip(variables,observed)}})
report={"source":"https://jenvbs.journals.ekb.eg/article_54170_dd3f51abb5d4b2a15ee54215c93d8298.pdf",
        "locator":"Table2 printedpage149", "months":len(comparisons),"comparisons":comparisons,
        "mean_monthly_bias":{key:st.mean(r["differences_power_minus_published"][key] for r in comparisons) for key in variables},
        "monthly_mae":{key:st.mean(abs(r["differences_power_minus_published"][key]) for r in comparisons) for key in variables},
        "interpretation":"Diagnostic only: one published table, no original station archive/QC or exact station exposure metadata. Differences are material and do not establish which source is right. Pan evaporation in that table is not ET0 and was not compared with calculated ET0. No bias correction fitted."}
(root/"station_table_diagnostic.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
print(json.dumps({k:v for k,v in report.items() if k!="comparisons"},indent=2))
