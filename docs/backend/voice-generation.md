# Generating the app's voice with ElevenLabs

**Read this if…** you will produce, check or replace the app's spoken audio, or wire the text-to-speech provider.

Status: Proposed 13 Nov 2026 · Owner: Yahya (pipeline), **Moaaz (runs the generation and the listening review, from 14 Nov)**, Amr (voice sign-off) · Last reviewed 14 Nov 2026.

Fills the provider slot left open in [backend design §9 (D7)](backend-design.md#9-voice-output-d7). **ElevenLabs is used offline only: all audio is generated ahead of time; the running app never calls ElevenLabs** (Yahya, 13 Nov 2026). Spoken wording comes from the templates in [§7](backend-design.md#7-bilingual-design-d4); voice behaviour on screen is in [design/voice-first.md](../design/voice-first.md). Nothing here has been run yet: the scripts below are planned, not written.

---

> **Update 14 Nov 2026 (Yahya):** the app's voice is built by [`backend/scripts/voice_build/`](../../backend/scripts/voice_build/README.md): every spoken sentence is listed once in `frontend/src/voice/catalogue.json` (+ backend templates), recorded with pauses where changing words go, cut into pieces, and played piece + word + piece in the browser from `frontend/public/audio/`. This replaces the per-scenario generation in §2 and the `/speech/tts` lookup for playback (§5). Sections below still apply to voice choice (§3) and wording (§4).

## 1. When to generate

Generation is a **release step**, run once the inputs are final. Don't generate audio for draft wording.

| Gate | Done when | Who |
|---|---|---|
| Templates frozen | Every spoken line exists as a code in `data/release/content/messages.{ar-EG,en}.json` with a `speech` variant and a `version` | Yahya |
| Arabic reviewed | A native Egyptian speaker has read every Arabic `speech` line aloud and approved it | Amr arranges |
| Scenarios final | Every demo scenario (UH-001; SB-001 once supplied) runs through the real planner and returns its results | Karim / Yahya |
| Voices chosen | One Arabic and one English voice signed off (§3) and recorded in `voice.json` | Amr |

Regenerate only what changed (§6). The cache key makes this automatic.

## 2. What gets generated

**Rule: every spoken sentence comes from a template code plus parameters. No hand-typed sentences are sent to ElevenLabs.** Dynamic sentences come from **real planner outputs** for each scenario, never from sentences written to look like results.

| Kind | Examples (lab where they appear) | Source | Generated |
|---|---|---|---|
| Fixed prompts | “What will you grow in season 1?”, “Which year?” (02) | `question_id` templates, no params | Once per locale |
| Voice-dock and recovery lines | “I didn't hear anything…”, “Microphone is off…” (00) | Recovery templates, no params | Once per locale |
| Help and redirects | “I cannot recommend a crop on my own…” (04, 05) | Fixed templates | Once per locale |
| Readbacks | “Season 1: berseem, animal feed. Last cut 20 May 2027. Is that right?” (03) | Template + confirmed scenario facts | Per scenario |
| Results | Conflict sentence, why-sentence, zero-alternatives sentence (04, 05) | `{code, params}` returned by the Promise Test | Per scenario |
| Takeaway | “The berseem cut on 20 May is kept in the plan…” (08) | Evidence Card takeaway template | Per scenario |

The lab files under `work/ux-phase-4/` contain **draft** wording for review. Move approved lines into the message catalogue; don't generate from the lab files.

Lines spoken only by the frontend (voice-dock states) also live in the backend catalogue, so one reviewed source feeds both the screen text and the audio (D4).

## 3. Choosing the voices

1. **List the models available on the account** (`GET /v1/models`) and pick one that supports Arabic. The docs list Arabic for `eleven_multilingual_v2` and newer models; check the live list rather than this doc. Record the exact `model_id`.
2. **Arabic voice must sound Egyptian.** ElevenLabs describes its Arabic as Saudi/UAE, so the dialect comes from the voice, not the model. Shortlist 3 voices from the Voice Library filtered to Arabic/Egyptian, or a voice built with Voice Design. A cloned team voice needs that person's written consent.
3. **Audition set:** 10 lines covering a question, a full date with year (“خمستاشر مايو ألفين سبعة وعشرين”), all four crop names, “هكتار”, a “needs review” line, the conflict sentence and the takeaway. Generate each shortlisted voice with the same settings and seed.
4. **Listen as a group**, then ideally with 2–3 Egyptian Arabic speakers who match the target users. Pick on: dialect, clear numbers and dates, calm adult tone, no English fallback. Amr signs off.
5. Repeat for one English voice (clear, neutral).
6. Record the result in `data/release/content/voice.json` (committed, no secrets):

```json
{"ar-EG": {"voice_id": "<id>", "model_id": "<id>", "voice_settings": {"stability": 0.0, "similarity_boost": 0.0, "style": 0.0, "use_speaker_boost": true}, "seed": 0, "output_format": "mp3_44100_128"},
 "en":    {"voice_id": "<id>", "model_id": "<id>", "voice_settings": {}, "seed": 0, "output_format": "mp3_44100_128"}}
```

The zeros are placeholders. Fill them with the values chosen in the audition.

## 4. Writing text that speaks well

- Use the `speech` variant, never the `text` variant: numbers and dates spelled as Egyptian words by `i18n/formatting.py` (§7.4), no digits, no ISO dates, no Latin letters in Arabic lines.
- Short sentences (design rule: one idea per prompt). Long takeaways are split into sentences and generated per sentence, then played in order.
- Fix mispronunciations in the template spelling first (e.g. add a diacritic). If that fails, try a pronunciation dictionary, but check first that the chosen model supports one, because the docs don't confirm this per model.
- Keep units as spoken (“واحد هكتار”); never convert silently.

## 5. The generation run (planned)

`backend/scripts/build_prompt_audio.py` (named in D7) does the whole run:

1. Load `messages.*.json`, `voice.json` and each scenario fixture; run the planner for each scenario and collect every `{code, params}` it returns.
2. Render each line's `speech` text per locale.
3. Cache key = SHA256 of `locale + voice_id + model_id + settings + seed + template_version + speech text` (extends D7's key with the model and settings, so changing any of them makes new files).
4. **`--dry-run`** prints every line, its key, whether it's already cached, and the total character count (ElevenLabs bills by characters). Run this first and check the count against the account's quota.
5. For each missing key, call `POST /v1/text-to-speech/{voice_id}` with `model_id`, `voice_settings`, `seed` and `output_format`. Retry on rate limits with backoff; stop on any other error.
6. Write `frontend/public/audio/{locale}/{key8}.mp3` and append to `audio-manifest.json`: key, code, params, locale, speech text, voice, model, characters, created date.
7. Normalise loudness so prompts play at the same volume, e.g. `ffmpeg -i in.mp3 -af loudnorm=I=-16:TP=-1.5:LRA=11 out.mp3`.

`scripts/prewarm_audio.py` (D7) becomes a mode of the same script that covers only UH-001, for the offline demo.

**At runtime nothing is generated.** `POST /speech/tts` only looks up the pre-generated file for `{code, params, locale}` by its cache key. Lookup order: pre-generated file → device voice labelled “device voice” → text with “audio unavailable”. The backend holds no ElevenLabs key and makes no provider call. The client still sends only `{code, params}`, never free text.

**Consequence:** a sentence that wasn't generated (for example, a farmer's own plan outside the prepared scenarios, with dates nobody generated) has no ElevenLabs audio. See open question 4.

## 6. Check every file before release

Listen to all generated files, not a sample. For each one, check:

- [ ] Egyptian dialect throughout; no MSA or Gulf drift on key words
- [ ] Dates say day, month **and year**; numbers match the screen
- [ ] Crop names, “هكتار”, “محتاج مراجعة زراعية” are clear
- [ ] No English fallback, clipped endings or long silences
- [ ] Status meaning is right: “needs review” never sounds like approval; “saved” only on the saved line
- [ ] Same loudness as neighbouring prompts

Log rejects in the manifest with a reason and regenerate with a different seed or fixed spelling. The listening check is not farmer-comprehension testing; that is still design.md §8.

**Regenerate when** a template's `version` changes, a scenario's results change, or `voice.json` changes. The new key makes new files; stale audio is never played for a new plan version (D7).

## 7. Keys, privacy and storage

- `ELEVENLABS_API_KEY` is needed only on the machine that runs the generation script (a local `.env`, git-ignored). It is never deployed with the backend or frontend, and never committed, logged or written in docs.
- **Only template text for fictional scenarios is ever sent to ElevenLabs**, at generation time. No farmer data reaches it, because the app never calls it. Zero-retention mode (`enable_logging=false`) is enterprise-only; on other plans, assume ElevenLabs keeps the generation requests.
- **Proposed:** generated `.mp3` files are git-ignored and shared like other release artifacts; `voice.json` and `audio-manifest.json` are committed, so anyone with a key can regenerate the exact set. Needs Amr's OK, because the repo rules forbid committing generated data.

## 8. Open questions

1. Which ElevenLabs plan and account, and who holds the key? (Budget owner: Amr.)
2. Voice Library voice, Voice Design voice, or a consenting team member's clone for Egyptian Arabic?
3. Commit the `.mp3` files for an offline demo, or ship them as a release artifact (§7)?
4. **Plans outside the prepared scenarios.** With no live generation, how do they get audio? Options: (a) pre-generate the reusable pieces (crop names, purposes, every day/month/year phrase, fixed sentence frames) and play them in sequence; (b) fall back to the labelled device voice for those sentences; (c) keep audio only for the prepared demo scenarios and say so. Option (a) keeps one voice but needs sentence frames written for splicing and a listening check of the joins. **(d), added 14 Nov 2026:** generate changing sentences live with ElevenLabs in the same voice and cache them (the app needs the network for Gemini anyway). Splicing word by word is likely to sound robotic in Arabic. **Yahya, 14 Nov: try (d) in a demo first, then decide.** Test kit: [`backend/scripts/voice_test/`](../../backend/scripts/voice_test/README.md) (3 sentences, both ways, blind X/Y). Until then the 13 Nov "offline only" decision stands. **Decided 14 Nov 2026 (Yahya): record each sentence once with a pause where each changing word goes, cut at the pauses, and record each changing word once** (a variant of (a) that keeps sentence intonation). Built: [`backend/scripts/voice_build/`](../../backend/scripts/voice_build/README.md). Generation stays offline; the app plays static files and needs no live TTS call.

Sources checked 13 Nov 2026: [Create speech](https://elevenlabs.io/docs/api-reference/text-to-speech/convert), [Models](https://elevenlabs.io/docs/overview/models), [Zero Retention Mode](https://elevenlabs.io/docs/eleven-api/resources/zero-retention-mode).
