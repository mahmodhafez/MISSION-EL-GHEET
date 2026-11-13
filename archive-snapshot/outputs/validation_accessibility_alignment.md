# MISSION EL GHEET: accessibility and challenge-alignment readiness

Review date: 10 November 2026. Scope: the supplied challenge statement and `MISSION_EL_GHEET_Final_Product_Decisions.md`. This is a documentary assessment and a proposed validation protocol. No speech service, model, private recording, farmer session or application was run. No subscription, dependency or account connection was added.

Evidence labels: **O** = observed in supplied material; **V** = verified in primary documentation opened in this session; **I** = design recommendation or inference. Documentation establishes advertised capability, not dialect accuracy or successful independent use.

## Readiness judgment

**O:** The agreed direction retains complete Arabic/English interaction, Egyptian speech, pictures, confirmation, recovery and a spoken takeaway as core requirements. It appropriately says independent usability by farmers who cannot read is untested. **I:** Preserve those requirements. The immediate gap is a demonstrated journey from an imperfect spoken statement to a correctly understood, explicitly approved plan. A microphone button, translated labels or a spoken introduction alone will not close it.

## Challenge alignment

The supplied challenge uses “may” for examples, including comparison of at least three strategies. Its central purpose is rotation decision support combining NASA Earth observations, local soil information, crop characteristics and farmer priorities. Treat optional examples as design guidance rather than mandatory contest rules. **O**

| Challenge connection | Existing direction | Readiness evidence still needed |
|---|---|---|
| NASA observations inform rotation exploration | POWER historical comparison; separate trained near-term outlook | Show which historical input changes an explanation or trade-off beyond a crop calendar. The next-week forecast must remain subordinate to the rotation task. |
| Local soil and crop characteristics matter | Soil restrictions, locally supported catalogue and crop rules | Changing a relevant soil input must change eligibility, required review or a sourced explanation. An unused intake field is insufficient. Unknown soil information must remain unknown. |
| Compare strategies and explain benefits/risks | Existing plan plus up to two feasible options, with explicit trade-offs | Aim for one reviewed case with three distinct crop sequences. Date-only changes are timing variants. Do not manufacture alternatives when constraints permit fewer. |
| Soil-health and resilience purpose | Sourced sequence indicators; no claim of measured improvement | Explain a locally applicable sequence mechanism, such as a legume opportunity or residue/cover consideration, together with trade-offs. Do not infer soil improvement from greenness or ET0. |
| Farmer priorities and local expertise | Locked commitments, approval, adviser checks | Demonstrate that a forage commitment survives calculation, translation and correction. A farmer must understand what changed and what remains unresolved. |

These are proposed evidence checks, not findings that the application already passes. **I**

## One practical speech candidate

**I — candidate for the first bounded trial, not an adopted architecture:** use the existing Azure Speech standard services for real-time recognition and synthesis, with an explicit Arabic/English selector. Use `ar-EG` recognition and `ar-EG-SalmaNeural` output for Egyptian Arabic; use `en-US` recognition and `en-US-JennyNeural` output for English. Keep the two language paths tied to the same structured facts and approvals. Use authored Egyptian-Arabic sentences; selecting an Egyptian voice does not translate formal Arabic into natural Egyptian wording.

**V:** Microsoft documents real-time speech recognition for `ar-EG` and `en-US`, and lists the selected voices. This supports a trial; it supplies no measured accuracy for Sakha farmers, local crop names, noisy fields or the project's tasks. [S1]

**V:** The standard quickstarts use an existing baseline recognizer and prebuilt voice; custom speech or voice training is unnecessary. They require an Azure subscription, Speech resource and authorized credentials. [S2, S3] Regional endpoints and resource configuration matter, and available voices can be checked against the resource's voice-list endpoint. [S4, S6]

**I — access and resource gates:** first establish whether the team already has authorized service access, an acceptable region and sufficient quota. None was inspected here. Do not create a subscription or incur charges to remove this gate. Calls use hosted inference, so this candidate would not require loading a speech model onto the same 4 GB GPU used for the forecasting experiment; network latency, availability and cost still need measurement. No price or free-tier entitlement is assumed.

**Licensing status:** this proposal is a hosted-service route, not a verified open-weight/offline model licence. Microsoft Product Terms were opened, but the dynamic page did not expose the applicable account/program terms for review. Rights and conditions for service use and any retained generated audio remain an access gate; do not treat an SDK sample licence as a licence to the hosted model or voices. [S7]

**V/I — audio handling:** Microsoft's real-time STT documentation describes processing in server memory without storage at rest, unlike batch-transcription storage workflows. [S5] That does not authorize uploading a farmer's recording. Use consenting test speakers and fictitious field cases after the team's access is authorized; keep recording/transcript retention off by default in the application. Do not embed service secrets in the public interface.

### Recovery fallback

**I:** provide the same bounded journey through crop pictures, touch choices and team-recorded Egyptian-Arabic/English prompts, with repeat/back/change controls and adviser assistance. A selected picture is spoken before a separate confirmation. Cache approved prompts and, where permitted, generated result audio together with the exact plan version. A stale recording must never narrate a changed result. If a new numerical explanation cannot be spoken, say so through an available fixed prompt and offer retry/adviser assistance; do not substitute a previous result or silently rely on text.

This is an outage/recognition-recovery route, not permission to omit working spoken input/output from the main implementation. A complete offline product is not implied. If service access is unavailable, the main speech route remains unvalidated and requires an explicit replacement decision; a prerecorded demonstration does not establish live recognition.

## Required no-reading journey

All items below are proposed acceptance criteria. **I**

1. **Start and language:** one obvious start control plays a short welcome. Arabic and English choices have audio examples. Microphone permission denial has a spoken/picture recovery path. Language choice must not require reading a flag label.
2. **One fact at a time:** ask a short question about the crop, purpose, area, release date, water availability or priority. Permit “I do not know.” Distinguish grain maize, grain sorghum and forage crops through spoken names and locally recognizable pictures.
3. **Interpret without committing:** speech recognition and any structured extraction propose facts; they do not approve them. Preserve unknown, negotiable and protected states separately. Negation and correction must not be lost.
4. **Disambiguate dates and units:** expand a date into spoken day, month and year; resolve relative dates against the displayed issue date and Africa/Cairo timezone. Read area and its unit together. Ask what “قيراط” or an omitted unit means before conversion. A day/month string, missing year, or an impossible date is not silently repaired. Keep originals alongside confirmed normalized values.
5. **Confirm and correct:** play the interpreted fact, including negation and lock status. Provide separate large confirm, change, repeat and back controls. Spoken “no” or “I meant…” must reopen the relevant field. Silence, a timeout, an ASR confidence value or an unrelated “yes” is not approval. Changing a protected commitment requires its own explicit confirmation.
6. **Hear the comparison:** speak the unchanged commitment, conflict, permitted changes, important trade-offs and missing evidence in short chunks. Put historical replay and the experimental future outlook in separate labelled and spoken sections. Read the outlook's actual issue date and target dates; stale data cannot be described as “the coming week.”
7. **Approve the plan:** repeat the proposed sequence and actionable next step. Only explicit approval changes the saved plan. Correcting a critical input invalidates dependent comparisons and prior plan approval until recomputed and confirmed. Language switching preserves facts; if wording is corrected materially, reconfirm that fact.
8. **Take it away and recover:** the evidence card and spoken takeaway use the same confirmed plan version, dates, units and outstanding checks. A person can replay the next step, stop the audio, return without losing confirmed facts, and ask for help. An interrupted or failed save must be announced; do not claim the plan was saved without acknowledgement.

Use familiar crop pictures with audio labels; pictures alone are not automatically understandable. W3C guidance supports meaningful labels/instructions and explicit errors. Keep accessible text as well as speech for assistive technology and other users. [S9, S10] For this prototype, target at least 48 × 48 CSS-pixel primary touch controls with separation, keyboard access and visible focus; 48 is this review's design target, not a claimed WCAG minimum. W3C's minimum target criterion is 24 × 24 with exceptions, while its enhanced target criterion uses 44 × 44. [S8]

## Small meaningful evaluation protocol

**Proposed study, not completed evidence.** First run a scripted integration check, then an observed usability session. Do not ask participants to read the script as a substitute for natural speech.

**Speech set:** four consenting native Egyptian-Arabic speakers, ideally including the intended local speech community, each supplying 12 short, prompted utterances in their own wording: 48 recordings. Repeat those cases with realistic, non-disruptive background noise or collect a second noisy take: 96 total. Add two English speakers with 12 corresponding cases each. These counts are a manageable proposed engineering sample, not a statistical claim of population coverage. Keep at least one speaker and some paraphrases unseen while adjusting extraction rules. Any tested tuning set must be distinguished from the final check set.

| Case family | Example prompt/utterance | Correct behavior to inspect |
|---|---|---|
| Protected forage | “البرسيم لازم يفضل لحد آخر مايو.” | Ask year and what “آخر مايو” means operationally; preserve the protected commitment. |
| Explicit negation | “ما تشيلش البرسيم.” | Never extract permission to remove berseem. |
| Crop correction | “مش قمح، أنا قصدي برسيم.” | Replace the proposed crop with berseem; do not keep both. |
| Ambiguous crop | “هزرع درة.” | Ask maize or sorghum and grain or forage; speak picture choices. |
| Local area | “نص فدان”، “فدان إلا ربع”، “اتناشر قيراط” | Confirm magnitude and land-area unit; use no unsourced conversion. |
| Numeric date | “عشرة حداشر”، “١٠/١١” | Ask day/month/year and read the resolved date fully. |
| Relative date | “الجمعة الجاية”، “بعد العيد” | Confirm an explicit calendar date; do not infer a holiday or year silently. |
| Water restriction | “المية مش عندي غير يوم الخميس.” | Preserve restriction; obtain the relevant dated water turn. |
| Unknown soil | “مش عارف الملوحة كام.” | Store unknown and request review where needed, not zero salinity. |
| Value/unit correction | “مش اتنين، اتناشر. والفدان مش متر.” | Correct the intended field and replay the whole value with its unit. |
| Missing or confusing response | Silence, overlapping speakers, “مش فاكر” | No invented facts or automatic confirmation; offer repeat/picture/help. |
| Language switch and cancel | Arabic facts, English switch, then “ارجع، ما تحفظش” | Preserve facts, cancel the save, and explain the current state audibly. |

**Measure:** exact agreement for crop/purpose, date/year, amount/unit, negation, lock and explicit approval; clarification frequency; corrections needed; successful recovery; time to understood confirmation; and end-to-end latency. Word-error rate is a diagnostic only: a fluent transcript with one missing negation can be the more serious failure. Do not conceal an error through forgiving text normalization when it changes a crop, number or meaning.

**Output comprehension:** have listeners repeat the interpreted date, crop, unit and next step in their own words, or select the corresponding picture/action. Include comparisons containing different dates, an unknown value, no feasible alternative, a protected commitment, a stale outlook and a changed numerical result. Check the English counterpart for identical facts and approvals, not merely similar wording.

**No-reading usability:** observe at least three consenting intended users who cannot comfortably use written app instructions, including a farmer where possible. Use fictitious cases without requiring anyone to disclose literacy or personal farm data. Tasks: enter a commitment; correct a deliberately wrong date; compare options; reject a forbidden change; approve and replay a takeaway; recover from lost connectivity. Do not coach during the independent portion. Log every hint and repeat the failed task after any revision. Three participants are a formative check, not evidence of general accessibility. A literate team member hiding the text is useful rehearsal but does not replace intended-user evidence.

**Decision gates:** any unconfirmed change to crop, protected commitment, date, unit or approved plan is a stop-and-fix defect for that flow. Every scripted ambiguity must either resolve correctly after explicit confirmation or remain unresolved without committing. Report first-pass accuracy and assisted/independent task completion as observed counts, without inventing pass percentages. Independent-usability claims remain closed until intended users complete the full journey and explain the result without reading or coaching; even then, limit the claim to the tested sample and conditions.

## Remaining gates and ownership

| Gate | Evidence required | Suggested owner |
|---|---|---|
| Authorized speech access | Existing resource/region, selected voices available, quota and applicable terms checked | DevOps member and project lead |
| Egyptian wording and pronunciation | Human review of crop names, units, dates, negation and result speech | Product lead plus Egyptian-Arabic test speakers |
| Correct structured facts | Scripted cases, confirmation/correction audit and plan-version consistency | Software reviewer and builder |
| Complete bilingual recovery | Same facts and approval state after switches, errors, cancellation and reconnection | Builder and software reviewer |
| Independent no-reading journey | Observed intended-user sessions, assistance log and comprehension evidence | Product lead; recruitment not performed here |
| Rotation and soil relevance | One locally reviewed case with meaningful sequences and a soil input that actually affects interpretation | Agronomic reviewer/extension engineer, with data analyst |

## Primary web sources

All links below were **OPENED on 10 November 2026**. S7 was accessible only as a partial dynamic page; applicable terms remain unverified. No citation is from memory.

1. **S1 — Microsoft, language and voice support:** https://learn.microsoft.com/en-us/azure/ai-services/speech-service/language-support?tabs=stt
2. **S2 — Microsoft, speech-to-text quickstart:** https://learn.microsoft.com/en-us/azure/ai-services/speech-service/get-started-speech-to-text
3. **S3 — Microsoft, text-to-speech quickstart:** https://learn.microsoft.com/en-us/azure/ai-services/speech-service/get-started-text-to-speech
4. **S4 — Microsoft, Speech regions:** https://learn.microsoft.com/en-us/azure/ai-services/speech-service/regions
5. **S5 — Microsoft, real-time STT data handling:** https://learn.microsoft.com/en-us/azure/foundry/responsible-ai/speech-service/speech-to-text/data-privacy-security
6. **S6 — Microsoft, TTS REST and voice list:** https://learn.microsoft.com/en-us/azure/ai-services/speech-service/rest-text-to-speech
7. **S7 — Microsoft Product Terms, Azure:** https://www.microsoft.com/licensing/terms/productoffering/MicrosoftAzure/all
8. **S8 — W3C, target size:** https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html
9. **S9 — W3C, labels and instructions:** https://www.w3.org/WAI/WCAG22/Understanding/labels-or-instructions.html
10. **S10 — W3C, error identification:** https://www.w3.org/WAI/WCAG22/Understanding/error-identification.html
