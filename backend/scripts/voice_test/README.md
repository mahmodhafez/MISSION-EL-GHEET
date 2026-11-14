# Voice test: whole sentence vs. swapped words

**For Moaaz.** About 30 minutes, and about 650 ElevenLabs characters.

## Why

The app has to say sentences that change with each farmer's plan, for example "sowing the maize on 15 May comes before the
berseem cut on 20 May". We can't record every possible date and crop ahead of time. There are two ways to do it:

- **Whole sentence:** ElevenLabs makes the full sentence when the app needs it. One natural sentence, but it costs a call.
- **Swapped words:** we record each sentence once, then cut out only the words that change (crop, date) and drop in
  recordings of the new words. Free at runtime, but the joins may be audible.

This test makes **both versions of the same 3 Arabic sentences, in the same voice**, so we can hear the difference before
deciding. The script does the cutting itself: ElevenLabs returns where each letter falls in the audio, so it knows where to cut.

## Steps

1. **Pick the Egyptian Arabic voice** you'd use for the app (Voice Library or Voice Design). Copy its **voice ID**.
2. **Install ffmpeg** if you don't have it (`ffmpeg -version` should work in a terminal). Python 3 is the only other thing needed.
3. **Check the plan** (calls nothing):
   ```sh
   python make_samples.py --dry-run
   ```
4. **Generate**: set the key and voice, then run. Don't paste the key into any file or chat.

   macOS / Linux:
   ```sh
   export ELEVENLABS_API_KEY=...   ELEVENLABS_VOICE_ID=...
   python make_samples.py
   ```
   Windows PowerShell:
   ```powershell
   $env:ELEVENLABS_API_KEY="..."; $env:ELEVENLABS_VOICE_ID="..."
   python make_samples.py
   ```
   Optional: `ELEVENLABS_MODEL_ID` (default `eleven_multilingual_v2`) and `ELEVENLABS_VOICE_SETTINGS`, e.g.
   `{"stability":0.5,"similarity_boost":0.75}`. Use the same values you'd use for the real app audio.
5. **Listen blind.** Open `out/listen/`: each sentence has an **X** and a **Y** file. One is the whole sentence, the other has
   swapped words, in random order. **Don't open `out/answer_key.txt` yet.** Ideally 2–3 Egyptian Arabic speakers listen, not
   only the team.
6. **Score** each pair in the table below, then open the answer key and fill in the last column.

## Score sheet (copy into your reply)

| Sentence | Natural? X (1–5) | Natural? Y (1–5) | Which sounds like one person talking normally? | Any word said wrong? | Which was swapped? (from key) |
|---|---|---|---|---|---|
| 01 conflict | | | | | |
| 02 readback | | | | | |
| 03 option | | | | | |

Also send:
- The **"time to generate each whole sentence"** numbers the script prints at the end. That's how long a farmer would wait the first time.
- The voice ID, model and settings you used (IDs only, never the API key).
- Your gut call in one line: would you ship the swapped version?

## What we'll decide from it

If listeners can't reliably tell which one is swapped and score it 4+, we swap (cheaper, works offline). Otherwise we generate
whole sentences live and cache them. Decision recorded by Yahya in `docs/decisions.md`.

## Notes

- Each sentence is recorded once with one plan's values, then the new plan's words are swapped in (see `sentences.json`).
  The new values are a made-up plan for listening only. Sentence 2 is **draft** readback wording. Comment on wording too if
  something sounds wrong to an Egyptian ear, but don't change `sentences.json`; send notes instead.
- If a cut lands slightly off (a clipped letter, a bit of the old word left), note which sentence. That's useful data too.
- Files land in `out/`, which git ignores. **Don't commit any `.mp3`.** Re-running reuses files already made; `--fresh` starts over.
- `--fake` makes beeps instead of speech, to check ffmpeg works without spending characters.
