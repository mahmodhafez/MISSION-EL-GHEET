"""Voice listening test: whole sentence vs. "record once, swap the changing words", same voice.

A = the whole sentence generated with the new values (what live generation would sound like).
B = the sentence generated ONCE with other values (the frame); the changing words are cut out using
    ElevenLabs character timings and replaced with separately generated clips of the new values.

Standard library only; needs ffmpeg/ffprobe on PATH. See README.md in this folder.

    python3 make_samples.py --dry-run        # show the plan and the character count; calls nothing
    python3 make_samples.py                  # generate (needs ELEVENLABS_API_KEY and ELEVENLABS_VOICE_ID)
    python3 make_samples.py --fake           # check the pipeline offline with beeps instead of speech
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import random
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
API = "https://api.elevenlabs.io/v1/text-to-speech/{voice}/with-timestamps?output_format=mp3_44100_128"
SLOT = re.compile(r"\{(\w+)\}")


def run(cmd: list[str]) -> str:
    return subprocess.run(cmd, check=True, capture_output=True, text=True).stdout


def duration(f: Path) -> float:
    return float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(f)]).strip())


def tts(text: str, cfg: dict, dest: Path, fake: bool) -> tuple[dict, float]:
    """Write one MP3 for `text`; return (alignment, seconds the request took). Cached next to the MP3."""
    meta = dest.with_suffix(".json")
    if dest.exists() and meta.exists():
        return json.loads(meta.read_text(encoding="utf-8")), 0.0
    t0 = time.monotonic()
    if fake:  # a beep as long as the text would roughly take; timings spread evenly over the characters
        secs = max(0.3, len(text) / 15)
        run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", f"sine=frequency=440:duration={secs:.2f}", "-ac", "1", "-ar", "44100", str(dest)])
        step = secs / len(text)
        align = {"characters": list(text), "character_start_times_seconds": [i * step for i in range(len(text))],
                 "character_end_times_seconds": [(i + 1) * step for i in range(len(text))]}
    else:
        body = {"text": text, "model_id": cfg["model_id"], "seed": cfg["seed"]}
        if cfg.get("voice_settings"):
            body["voice_settings"] = cfg["voice_settings"]
        req = urllib.request.Request(API.format(voice=cfg["voice_id"]), data=json.dumps(body).encode(), method="POST",
                                     headers={"xi-api-key": cfg["key"], "Content-Type": "application/json"})
        for attempt in range(4):
            try:
                with urllib.request.urlopen(req, timeout=60) as r:
                    data = json.loads(r.read())
                break
            except urllib.error.HTTPError as e:
                if e.code == 429 and attempt < 3:
                    time.sleep(2 ** attempt * 2)
                    continue
                sys.exit(f"ElevenLabs error {e.code} for {text!r}: {e.read()[:300].decode(errors='replace')}")
        dest.write_bytes(base64.b64decode(data["audio_base64"]))
        align = data.get("alignment") or {}
    secs = time.monotonic() - t0
    meta.write_text(json.dumps(align, ensure_ascii=False), encoding="utf-8")
    return align, secs


def span(align: dict, text: str, start: int, end: int) -> tuple[float, float]:
    """Audio start/end (seconds) of text[start:end], from the character timings."""
    chars = "".join(align.get("characters", []))
    if chars != text:  # timings may skip or merge characters; find the words in what was aligned
        word = text[start:end]
        start = chars.find(word)
        if start < 0:
            sys.exit(f"Could not find {word!r} in the timings for {text!r}.")
        end = start + len(word)
    return align["character_start_times_seconds"][start], align["character_end_times_seconds"][end - 1]


def fill(template: str, values: dict) -> tuple[str, list[tuple[str, int, int]]]:
    """Template + values → sentence, plus where each slot landed (name, start, end) in the sentence."""
    out, spans, pos = "", [], 0
    for m in SLOT.finditer(template):
        out += template[pos:m.start()]
        v = values[m.group(1)]
        spans.append((m.group(1), len(out), len(out) + len(v)))
        out += v
        pos = m.end()
    return out + template[pos:], spans


def swap(frame: Path, frame_align: dict, frame_text: str, spans: list, clips: dict[str, Path], gap_ms: int, dest: Path) -> None:
    """Cut the slot words out of the frame and put the new clips in their place."""
    total = duration(frame)
    parts, t = [], 0.0  # (file, start, end)
    for name, s, e in spans:
        a, b = span(frame_align, frame_text, s, e)
        parts.append((frame, t, a))
        parts.append((clips[name], None, None))
        t = b
    parts.append((frame, t, total))
    inputs, filt, labels = [], [], []
    for i, (f, a, b) in enumerate(parts):
        inputs += ["-i", str(f)]
        trim = f"atrim={a:.3f}:{b:.3f},asetpts=PTS-STARTPTS," if a is not None else ""
        # short fades so cuts don't click
        filt.append(f"[{i}:a]{trim}aresample=44100,aformat=channel_layouts=mono,afade=t=in:d=0.01,areverse,afade=t=in:d=0.01,areverse[p{i}]")
        labels.append(f"[p{i}]")
    n = len(parts)
    if gap_ms:
        inputs += ["-f", "lavfi", "-t", f"{gap_ms / 1000:.3f}", "-i", "anullsrc=r=44100:cl=mono"]
        filt.append(f"[{n}:a]asplit={n - 1}" + "".join(f"[g{i}]" for i in range(n - 1)))
        seq, count = "".join(labels[i] + (f"[g{i}]" if i < n - 1 else "") for i in range(n)), 2 * n - 1
    else:
        seq, count = "".join(labels), n
    filt.append(f"{seq}concat=n={count}:v=0:a=1[out]")
    run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", ";".join(filt), "-map", "[out]", "-ac", "1", "-b:a", "128k", str(dest)])


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true", help="print the plan and character count; call nothing")
    ap.add_argument("--fake", action="store_true", help="beeps instead of ElevenLabs, to check ffmpeg and the folders")
    ap.add_argument("--fresh", action="store_true", help="delete out/ first (otherwise generated files are reused)")
    args = ap.parse_args()

    data = json.loads((HERE / "sentences.json").read_text(encoding="utf-8"))
    sents, gap = data["sentences"], data.get("gap_ms", 30)
    plan = []
    for s in sents:
        frame_text, spans = fill(s["template"], s["recorded"])
        new_text, _ = fill(s["template"], s["new"])
        plan.append((s, frame_text, spans, new_text))
    slot_values = sorted({v for s in sents for v in s["new"].values()})
    chars = sum(len(f) + len(n) for _, f, _, n in plan) + sum(len(v) for v in slot_values)
    print(f"{len(sents)} sentences, {len(slot_values)} swap-in clips, about {chars} characters billed.")
    if args.dry_run:
        for s, frame_text, _, new_text in plan:
            print(f"\n{s['id']}\n  recorded once: {frame_text}\n  swap in:       {', '.join(f'{k} → {v}' for k, v in s['new'].items())}\n  compare with:  {new_text}")
        return

    for tool in ("ffmpeg", "ffprobe"):
        if not shutil.which(tool):
            sys.exit(f"{tool} not found on PATH. Install ffmpeg, then run again.")
    cfg = {"key": os.environ.get("ELEVENLABS_API_KEY", ""), "voice_id": os.environ.get("ELEVENLABS_VOICE_ID", ""),
           "model_id": os.environ.get("ELEVENLABS_MODEL_ID", "eleven_multilingual_v2"), "seed": int(os.environ.get("ELEVENLABS_SEED", "1234"))}
    vs = os.environ.get("ELEVENLABS_VOICE_SETTINGS")  # optional JSON, e.g. {"stability":0.5,"similarity_boost":0.75}
    cfg["voice_settings"] = json.loads(vs) if vs else None
    if not args.fake and not (cfg["key"] and cfg["voice_id"]):
        sys.exit("Set ELEVENLABS_API_KEY and ELEVENLABS_VOICE_ID (see README.md), or use --dry-run / --fake.")

    if args.fresh and OUT.exists():
        shutil.rmtree(OUT)
    tag = "fake" if args.fake else hashlib.sha256(json.dumps([cfg["voice_id"], cfg["model_id"], cfg["seed"], cfg["voice_settings"]]).encode()).hexdigest()[:8]
    gen, listen = OUT / "generated", OUT / "listen"
    for d in (gen, listen):
        d.mkdir(parents=True, exist_ok=True)
    name = lambda text: gen / f"{hashlib.sha256((tag + text).encode()).hexdigest()[:12]}.mp3"

    clips = {v: name(v) for v in slot_values}
    for v, f in clips.items():
        tts(v, cfg, f, args.fake)

    rng, timings = random.Random(7), []
    key_lines = ["Answer key: do NOT open until everyone has scored.", ""]
    for s, frame_text, spans, new_text in plan:
        frame_align, _ = tts(frame_text, cfg, name(frame_text), args.fake)
        whole = name(new_text)
        _, secs = tts(new_text, cfg, whole, args.fake)
        if secs:
            timings.append((s["id"], secs))
        swapped = OUT / f"{s['id']}_{tag}_swapped.mp3"
        swap(name(frame_text), frame_align, frame_text, spans, {k: clips[v] for k, v in s["new"].items()}, gap, swapped)
        x_whole = rng.random() < 0.5
        shutil.copy(whole if x_whole else swapped, listen / f"{s['id']}_X.mp3")
        shutil.copy(swapped if x_whole else whole, listen / f"{s['id']}_Y.mp3")
        key_lines.append(f"{s['id']}: X = {'whole sentence' if x_whole else 'swapped words'}, Y = {'swapped words' if x_whole else 'whole sentence'}")
    (OUT / "answer_key.txt").write_text("\n".join(key_lines) + "\n", encoding="utf-8")

    print(f"\nListen to the pairs in {listen}  (X/Y order is random; answer key in {OUT / 'answer_key.txt'})")
    if timings:
        print("Time to generate each whole sentence (what a farmer would wait the first time):")
        for sid, secs in timings:
            print(f"  {sid}: {secs:.1f} s")


if __name__ == "__main__":
    main()
