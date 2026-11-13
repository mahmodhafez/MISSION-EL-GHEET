# Missing, excluded and not-yet-created artifacts

## Required existing computational evidence

All required raw POWER responses, derived ET0 files, audit/check scripts, base checkpoint/config, accepted LoRA adapters, training/evaluation source, frozen package list, metrics, predictions and protocol were found. See the manifest for exact files. Other saved failed/diagnostic runs are retained too.

## Local source-copy gaps

`work/agronomy/` contains download failure records, not the requested PDFs. Missing attempted files include `aiad_2019.pdf`, `sugita_2017.pdf`, `egyptian_clover_fao.pdf`, and `maize_arc.pdf`. Errors include HTTP 403/503, timeout and closed connection. Other online references cited by the specifications (including the later maize bulletin, Darwesh, Kubota and sorghum sources) are not saved as local copies in these artifact directories. Links/locators remain in the scientific documents. ASCE PDF/text are included. No sources were redownloaded for packaging.

## Not created or not separately preserved

- No locally validated crop catalogue, complete Kc/stage data, field soil survey, raw station/lysimeter benchmark, farmer interview or speech/usability result.
- No application/planner implementation, automated scenario acceptance results, real-time forecast vintage archive or fresh follow-up experiment.
- No separate saved pre-fix training-script version for the failed smoke run; current source contains the correction. No optimizer/scheduler checkpoint for exact mid-training resume.
- No standalone script for the separately reported independent all-row equation review was located; its written audit is included. The main ET0 calculation/test source and saved numerical audit are included.
- No exact offline environment image, dependency-wheel bundle or driver installer. Frozen versions and setup instructions are included. The base-model upstream model card/license file was not downloaded separately; provenance URLs and library LICENSE/NOTICE are included. Check upstream terms before external redistribution.

## Deliberate exclusions

The installed virtual environment (except existing Chronos LICENSE/NOTICE), caches, temporary files and Python bytecode are excluded. They add bulk and machine-specific state rather than research evidence. Unrelated submitted videos/PDFs and attachments are not validation artifacts. Existing Markdown audit/specification files are preserved unchanged; their historical status language is explained in REPRODUCE.md. New HANDOFF and REFERENCE_SCENARIO copies are included for context.
