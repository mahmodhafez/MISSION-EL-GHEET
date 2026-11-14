# Building the app's voice

**For Moaaz (media) and whoever changes spoken wording.** How every sentence the app says gets real audio.

## How it works

- Every sentence is recorded **once**, with a **pause (⏸) where a changing word goes**: "زراعة ⏸ يوم ⏸ قبل حشة ⏸ …".
  The script cuts it at the pauses into pieces.
- Every changing word is recorded **once on its own**: crops, purposes, seasons, numbers 1–31, months, years 2025–2030,
  day counts ("سبع أيام").
- The app plays pieces and words in order: "زراعة" + "الذرة الشامية" + "يوم" + "خمستاشر" + "مايو" + …
- A sentence with no recording (or a word missing) is spoken by the phone's own voice, labelled "Device voice". Nothing breaks.

What gets said comes from one list: [`frontend/src/voice/catalogue.json`](../../../frontend/src/voice/catalogue.json)
(screen sentences) plus the backend templates in `backend/app/i18n/messages.json`, combined into
`frontend/src/voice/voice-index.json`. About 64 Arabic and 66 English sentences plus their words; about 8,000 characters.

## Make the audio (ElevenLabs)

Needs Python 3 and ffmpeg. From the repo root:

```sh
python3 -I backend/scripts/voice_build/build_voice.py --sheet          # see everything that will be said (out/recording-sheet.md)
export ELEVENLABS_API_KEY=...  ELEVENLABS_VOICE_ID_AR=...  ELEVENLABS_VOICE_ID_EN=...
python3 -I backend/scripts/voice_build/build_voice.py --generate        # makes only what is missing
```

Optional: `ELEVENLABS_MODEL_ID` (default `eleven_multilingual_v2`), `ELEVENLABS_VOICE_SETTINGS` (JSON), `ELEVENLABS_SEED`.
The pauses are sent as `<break time="0.8s" />`. Use a model that supports break tags (check ElevenLabs' docs for the
model you pick). Windows PowerShell: `$env:ELEVENLABS_API_KEY="..."` and so on.

## Or record by voice

1. Run `--sheet`. Each row has a **file name** and what to say; **⏸ = stop for about a second, then carry on**.
2. Record each sentence in one take, calm and even, and each word on its own. Save as `<file name>.wav` (or .mp3/.m4a/.ogg) in one folder.
3. `python3 -I backend/scripts/voice_build/build_voice.py --recordings path/to/folder`

## Or import clips that were already cut

When the clips were made and cut elsewhere (e.g. `catalogue_voice_ar.zip`: `pieces/<key>.mp3`, plus `jobs.json` and
`overrides.json`), unzip it **outside the repo** and run:

```sh
python3 -I backend/scripts/voice_build/build_voice.py --import path/to/catalogue_voice --voice "ElevenLabs Fatima, Eleven v4"
```

The file name is the clip key (a hash of locale + text), so the script knows which piece or word each file is and skips any
that the current index no longer uses. It also skips clips that don't decode, last under 0.15 s or are near-silent, and
clips cut only from lines that `overrides.json` lists under `_regenerate`. Skipped clips are listed in `out/report.txt`.

## Check, then listen

- The script prints how many clips exist and writes `out/report.txt` for any sentence where it couldn't find the right
  number of pauses. Re-record or regenerate just those (delete their files in `frontend/public/audio/<ar|en>/` first, or use `--fresh` for everything).
- Run the app (`cd frontend && corepack pnpm dev`) and go through it with sound on. Listen for clipped words and odd joins.
- `--generate --fake` makes beeps instead of speech, to test the pipeline without spending characters.

## When wording changes

Edit the sentence in the screen code **and** in `catalogue.json` (or in `messages.json` for backend sentences), then:

```sh
python3 -I backend/scripts/voice_build/build_voice.py --index      # rebuild the index (frontend tests check every line)
python3 -I backend/scripts/voice_build/build_voice.py --generate   # record only the new pieces
```

In development the browser console prints `[voice] not in catalogue: …` for any spoken sentence that isn't in the list.

## Known gaps

- The **Season Replay summary** sentence (decimals like "10.2 درجة", "الـ14 يوم") isn't in the catalogue yet; it uses the device voice.
- Audio files in `frontend/public/audio/` **are committed** (14 Nov) so the deployed app plays them. `--check` also fails if
  `manifest.json` lists a clip that isn't on disk.
- **Shipped 14 Nov:** 75 Arabic clips (sentence pieces only). Still missing: every Arabic word clip (102: crops, numbers,
  months, years, day counts), so sentences with a changing word use the device voice; the 7 research lines; re-records of
  `why.local`, `options.found_one`, `api.dates_to_check` (one of their clips was silent); all English audio.
- The zip's clips were made with full stops as pauses (“dot method”, Eleven v4), not `<break>` tags.
