# Locating the archived experiment

In VALIDATION_ARTIFACTS.zip, prefix the paths below with `work/validation_2026-11-10/model_test/`. Each original file is covered by the archive's ARTIFACT_MANIFEST.json. The original archive SHA256 is `d284b3162a2dd5bbde8bcb37ae3090adcf080a5d044a4e25b2c96836b4cee95f`.

| Evidence | Archive member(s) |
|---|---|
| Local fit | run_model_test.py, installed_requirements.txt, checkpoint/config.json, checkpoint_provenance.json |
| Base weights | checkpoint/model.safetensors, SHA256 `ddcda3c7508bf2528087723e98a20707cc04b7f370ae275a9fd88078ddba4f42` |
| Pinned model revision | amazon/chronos-2 at `29ec3766d36d6f73f0696f85560a422f50e8498c` |
| Accepted runs | smoke20_verified/ and adaptation200/, each with results.json, diagnostic_predictions.npz and training/finetuned-ckpt/adapter_model.safetensors |
| Failed initial reload | smoke20/results.json and reload_diagnosis/result.json |
| Evaluation contract and consumed results | evaluation_protocol.json, evaluate_holdout.py, holdout_results.json, holdout_predictions.npz, verify_model_artifacts.py and artifact_verification.json |

The training code used the historical weather_et0.csv, two target channels and a float32 conversion. It selected adaptation200 by validation ET₀ MAE from the two accepted runs. The consumed July–October 2026 assessment is an archival comparison only. The 2022–2025 reserve has already been inspected. Unknown pretraining overlap and absent issue-time NASA vintages limit retrospective claims. Copies of selected small original records and the earlier audit's receipts are provided in the full project's provenance/experiment. Both original archives remain authoritative for historical execution.
