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
- Audio files land in `frontend/public/audio/` and are **not committed yet** (decision pending). The deployed app needs them in
  the build to play them.
