"""Build the app's voice: every sentence recorded once with pauses where the changing words go, cut at the
pauses into pieces; every changing word recorded once on its own. The app plays pieces and words in order.

Standard library only (+ ffmpeg/ffprobe on PATH for --generate / --recordings). Run from the repo root:

    python3 -I backend/scripts/voice_build/build_voice.py --index            # rebuild frontend/src/voice/voice-index.json
    python3 -I backend/scripts/voice_build/build_voice.py --check            # fail if the index is out of date (CI)
    python3 -I backend/scripts/voice_build/build_voice.py --sheet            # recording sheet + character count
    python3 -I backend/scripts/voice_build/build_voice.py --generate         # ElevenLabs (ELEVENLABS_API_KEY, ELEVENLABS_VOICE_ID_AR/_EN)
    python3 -I backend/scripts/voice_build/build_voice.py --generate --fake  # beeps instead of speech: checks the pipeline
    python3 -I backend/scripts/voice_build/build_voice.py --recordings DIR   # human recordings named as in the sheet
    python3 -I backend/scripts/voice_build/build_voice.py --import DIR       # clips already cut elsewhere, named <key>.mp3

See README.md in this folder.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))
from backend.app.i18n.formatting import AR_DIGITS, MONTHS, days, words, year_words  # noqa: E402

CATALOGUE = REPO / "frontend/src/voice/catalogue.json"
MESSAGES = REPO / "backend/app/i18n/messages.json"
INDEX = REPO / "frontend/src/voice/voice-index.json"
AUDIO = REPO / "frontend/public/audio"
OUT = Path(__file__).resolve().parent / "out"
LOCALES = {"ar": "ar-EG", "en": "en"}  # app locale → formatting locale
SLOT = re.compile(r"\{(\w+)\}")
PAUSE = "⏸"
YEARS = range(2025, 2031)
# Backend template params → slot kinds (messages.json uses descriptive param names).
PARAM_SLOT = {"crop": "crop", "cut_crop": "crop", "crop_bare": "crop", "cut_crop_bare": "crop", "crop_cap": "crop",
              "sowing_date": "date", "protected_cut_date": "date", "release_date": "date", "earliest_sowing_date": "date",
              "new_date": "date", "preparation_days": "days", "count": "num", "season_number": "num"}


def key(locale: str, text: str) -> str:
    return hashlib.sha256(f"{locale}|{text}".encode()).hexdigest()[:16]


def ar_digits(n: int) -> str:
    return "".join(AR_DIGITS[int(c)] for c in str(n))


# ---------------------------------------------------------------- index

def vocab(cat: dict) -> dict:
    """Per locale: slot kind → [{show, say, key}]. show = text as it appears; say = what is recorded."""
    out = {}
    for loc, floc in LOCALES.items():
        v: dict[str, list] = {}
        for kind, per in cat["vocab"].items():
            v[kind] = [{"show": w, "say": w} for w in per[loc]]
        nums = []
        for n in range(1, 32):
            say = words(n, floc)
            for show in {str(n), ar_digits(n) if loc == "ar" else str(n), say}:
                nums.append({"show": show, "say": say})
        v["num"] = nums
        v["month"] = [{"show": m, "say": m} for m in MONTHS[floc]]
        yrs = []
        for y in YEARS:
            say = year_words(y, floc)
            for show in {str(y), ar_digits(y) if loc == "ar" else str(y), say}:
                yrs.append({"show": show, "say": say})
        v["year"] = yrs
        v["days"] = [{"show": s, "say": days(n, floc, True)} for n in range(1, 31) for s in {days(n, floc, True), days(n, floc, False)}]
        for kind in v:  # unique shows, longest first (so "سبعة وعشرين" wins over "سبعة"), each with its clip key
            seen, items = set(), []
            for it in sorted(v[kind], key=lambda x: (-len(x["show"]), x["show"])):
                if it["show"] not in seen:
                    seen.add(it["show"])
                    items.append({**it, "key": key(loc, it["say"])})
            v[kind] = items
        out[loc] = v
    return out


def parts(template: str, loc: str) -> list[dict]:
    """Template → [{t: exact text, say, key} | {slot}]. say drops edge spaces and joining punctuation."""
    out, pos = [], 0
    for m in SLOT.finditer(template):
        if m.start() > pos:
            out.append(template[pos:m.start()])
        out.append({"slot": m.group(1)})
        pos = m.end()
    if pos < len(template):
        out.append(template[pos:])
    res = []
    for p in out:
        if isinstance(p, dict):
            res.append(p)
            continue
        say = p.lstrip(" :،,.؟?").rstrip(" :،,")
        res.append({"t": p, "say": say, "key": key(loc, say)} if say else {"t": p})
    return res


def backend_lines() -> list[dict]:
    msgs = json.loads(MESSAGES.read_text(encoding="utf-8"))["messages"]
    no_alt = msgs["no_feasible_alternative"]
    lines = []
    for code, m in msgs.items():
        if code.startswith("reason."):  # shown as picture labels, never spoken
            continue
        tpl = {loc: m[floc] for loc, floc in LOCALES.items()}
        variants = [("", tpl)]
        if code == "takeaway.conflict":  # {alternatives} is a whole sentence or nothing
            variants = [(".alt", {l: t.replace("{alternatives}", no_alt[LOCALES[l]]) for l, t in tpl.items()}),
                        (".noalt", {l: re.sub(r"\s*\{alternatives\}", "", t) for l, t in tpl.items()})]
        for suffix, t in variants:
            conv = {l: SLOT.sub(lambda mm: "{" + PARAM_SLOT.get(mm.group(1), mm.group(1)) + "}", s) for l, s in t.items()}
            lines.append({"id": f"api.{code}{suffix}", **conv})
    return lines


SKIPPED: set[str] = set()


def build_index() -> dict:
    cat = json.loads(CATALOGUE.read_text(encoding="utf-8"))
    voc = vocab(cat)
    kinds = set(voc["ar"]) | {"date"}
    index = {"_note": "GENERATED by backend/scripts/voice_build/build_voice.py --index from frontend/src/voice/catalogue.json and backend/app/i18n/messages.json. Do not edit.",
             "pause": PAUSE, "lines": {}, "vocab": voc}
    for loc in LOCALES:
        seen, out = set(), []
        for line in cat["lines"] + backend_lines():
            t = line[loc]
            bad = set(SLOT.findall(t)) - kinds
            if bad:  # e.g. a new backend param: that sentence keeps the device voice until PARAM_SLOT maps it
                SKIPPED.add(f"{line['id']}: unknown slot(s) {sorted(bad)}")
                continue
            if t in seen:
                continue
            seen.add(t)
            out.append({"id": line["id"], "parts": parts(t, loc)})
        index["lines"][loc] = out
    return index


def index_text(index: dict) -> str:
    return json.dumps(index, ensure_ascii=False, indent=1) + "\n"


# ---------------------------------------------------------------- what to record

def frames(index: dict, loc: str) -> list[dict]:
    """Unique sentences to record: the spoken pieces of each line, in order, joined by pauses."""
    out, seen = [], set()
    for line in index["lines"][loc]:
        pieces = [p for p in line["parts"] if p.get("say")]
        if not pieces:
            continue
        k = key(loc, PAUSE.join(p["say"] for p in pieces))
        if k in seen:
            continue
        seen.add(k)
        out.append({"id": line["id"], "file": f"{loc}_{k}", "pieces": pieces})
    return out


def word_list(index: dict, loc: str) -> list[dict]:
    seen, out = set(), []
    for kind, items in index["vocab"][loc].items():
        for it in items:
            if it["key"] not in seen:
                seen.add(it["key"])
                out.append({"kind": kind, "say": it["say"], "file": f"{loc}_{it['key']}", "key": it["key"]})
    return out


def sheet(index: dict) -> str:
    rows = ["# Recording sheet", "",
            f"Generated from the voice index. **{PAUSE} = stop for about one second, then carry on.** Read each sentence in one take, "
            "in a calm, even voice, and save it with the file name shown (any of .wav .mp3 .m4a .ogg). Words: one file per word.", ""]
    total = 0
    for loc in LOCALES:
        fr, wl = frames(index, loc), word_list(index, loc)
        rows += [f"## {'Arabic' if loc == 'ar' else 'English'}: {len(fr)} sentences", "", "| File | Say (" + PAUSE + " = pause) | Used for |", "|---|---|---|"]
        for f in fr:
            text = f" {PAUSE} ".join(p["say"] for p in f["pieces"])
            total += len(text)
            rows.append(f"| `{f['file']}` | {text} | {f['id']} |")
        rows += ["", f"### {'Arabic' if loc == 'ar' else 'English'} words: {len(wl)}", "", "| File | Say | Kind |", "|---|---|---|"]
        for w in wl:
            total += len(w["say"])
            rows.append(f"| `{w['file']}` | {w['say']} | {w['kind']} |")
        rows.append("")
    rows.insert(3, f"About {total} characters in total (ElevenLabs bills by character).\n")
    return "\n".join(rows) + "\n"


# ---------------------------------------------------------------- audio

def run(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, check=True, capture_output=True, text=True)


def duration(f: Path) -> float:
    return float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(f)]).stdout.strip())


def silences(f: Path) -> list[tuple[float, float]]:
    err = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(f), "-af", "silencedetect=noise=-38dB:d=0.35", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", err)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", err)]
    return list(zip(starts, ends))


TRIM = "silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse"


def encode(src: Path, dest: Path, start: float | None = None, end: float | None = None, trim: bool = True) -> None:
    cut = ["-ss", f"{start:.3f}", "-to", f"{end:.3f}"] if start is not None else []
    af = f"{TRIM},apad=pad_dur=0.06,loudnorm=I=-16:TP=-1.5:LRA=11" if trim else "loudnorm=I=-16:TP=-1.5:LRA=11"
    dest.parent.mkdir(parents=True, exist_ok=True)
    run(["ffmpeg", "-y", "-loglevel", "error", *cut, "-i", str(src), "-af", af, "-ac", "1", "-ar", "44100", "-b:a", "64k", str(dest)])


def cut_frame(src: Path, pieces: list[dict], loc: str, report: list[str], fid: str) -> int:
    """Split one recorded sentence at its pauses into the pieces' clips. Returns clips written."""
    n = len(pieces)
    if n == 1:
        encode(src, AUDIO / loc / f"{pieces[0]['key']}.mp3")
        return 1
    total = duration(src)
    inner = [s for s in silences(src) if s[0] > 0.1 and s[1] < total - 0.1]
    if len(inner) < n - 1:
        report.append(f"{fid}: expected {n - 1} pause(s), found {len(inner)}; not cut")
        return 0
    gaps = sorted(sorted(inner, key=lambda s: s[0] - s[1])[: n - 1])  # the n-1 longest pauses, in time order
    bounds = [0.0] + [x for g in gaps for x in g] + [total]
    for i, p in enumerate(pieces):
        a, b = bounds[2 * i], bounds[2 * i + 1]
        encode(src, AUDIO / loc / f"{p['key']}.mp3", max(0.0, a - 0.04), min(total, b + 0.06))
    return n


def eleven(text: str, voice: str, dest: Path) -> None:
    body = {"text": text, "model_id": os.environ.get("ELEVENLABS_MODEL_ID", "eleven_multilingual_v2"),
            "seed": int(os.environ.get("ELEVENLABS_SEED", "1234"))}
    if os.environ.get("ELEVENLABS_VOICE_SETTINGS"):
        body["voice_settings"] = json.loads(os.environ["ELEVENLABS_VOICE_SETTINGS"])
    req = urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{voice}?output_format=mp3_44100_128",
                                 data=json.dumps(body).encode(), method="POST",
                                 headers={"xi-api-key": os.environ["ELEVENLABS_API_KEY"], "Content-Type": "application/json"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                dest.write_bytes(r.read())
            return
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 3:
                time.sleep(2 ** attempt * 2)
                continue
            sys.exit(f"ElevenLabs error {e.code} for {text!r}: {e.read()[:300].decode(errors='replace')}")


def fake(pieces: list[str], dest: Path) -> None:
    """Beeps (one per piece, length ~ text) separated by 0.8 s of silence, like a recording with pauses."""
    inputs, labels = [], []
    for i, p in enumerate(pieces):
        inputs += ["-f", "lavfi", "-t", f"{max(0.3, len(p) / 15):.2f}", "-i", f"sine=frequency={400 + 40 * i}:sample_rate=44100"]
        labels.append(f"[{2 * i}:a]")
        if i < len(pieces) - 1:
            inputs += ["-f", "lavfi", "-t", "0.8", "-i", "anullsrc=r=44100:cl=mono"]
            labels.append(f"[{2 * i + 1}:a]")
    run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", f"{''.join(labels)}concat=n={len(labels)}:v=0:a=1,aformat=channel_layouts=mono[o]", "-map", "[o]", str(dest)])


def produce(index: dict, source: str, rec_dir: Path | None, fresh: bool) -> None:
    for tool in ("ffmpeg", "ffprobe"):
        if not shutil.which(tool):
            sys.exit(f"{tool} not found on PATH.")
    voices = {"ar": os.environ.get("ELEVENLABS_VOICE_ID_AR", ""), "en": os.environ.get("ELEVENLABS_VOICE_ID_EN", "")}
    if source == "eleven" and not (os.environ.get("ELEVENLABS_API_KEY") and all(voices.values())):
        sys.exit("Set ELEVENLABS_API_KEY, ELEVENLABS_VOICE_ID_AR and ELEVENLABS_VOICE_ID_EN (see README.md).")
    if fresh and AUDIO.exists():
        shutil.rmtree(AUDIO)
    report, made = [], 0
    raw = OUT / "raw"
    raw.mkdir(parents=True, exist_ok=True)

    def get(file: str, text_pieces: list[str]) -> Path | None:
        if source == "recordings":
            hits = [p for p in rec_dir.glob(f"{file}.*") if p.suffix.lower() in {".wav", ".mp3", ".m4a", ".ogg", ".flac"}]
            if not hits:
                report.append(f"{file}: no recording")
                return None
            return hits[0]
        dest = raw / f"{file}.mp3"
        if not dest.exists():
            if source == "fake":
                fake(text_pieces, dest)
            else:
                eleven(' <break time="0.8s" /> '.join(text_pieces), voices[loc], dest)
        return dest

    for loc in LOCALES:
        for f in frames(index, loc):
            if all((AUDIO / loc / f"{p['key']}.mp3").exists() for p in f["pieces"]):
                continue
            src = get(f["file"], [p["say"] for p in f["pieces"]])
            if src:
                made += cut_frame(src, f["pieces"], loc, report, f["file"])
        for w in word_list(index, loc):
            dest = AUDIO / loc / f"{w['key']}.mp3"
            if dest.exists():
                continue
            src = get(w["file"], [w["say"]])
            if src:
                encode(src, dest)
                made += 1
    write_manifest(index, made, report, source, {l: (voices[l] if source == "eleven" else source) for l in LOCALES},
                   os.environ.get("ELEVENLABS_MODEL_ID", "eleven_multilingual_v2") if source == "eleven" else None)


def write_manifest(index: dict, made: int, report: list[str], source: str, voice: dict, model: str | None) -> None:
    """List every clip on disk that the current index uses; the app only plays clips listed here."""
    used = {l: {p["key"] for f in frames(index, l) for p in f["pieces"]} | {w["key"] for w in word_list(index, l)} for l in LOCALES}
    keys = {loc: sorted(p.stem for p in (AUDIO / loc).glob("*.mp3") if p.stem in used[loc]) for loc in LOCALES if (AUDIO / loc).exists()}
    manifest = {"source": source, "voice": voice, "model": model, "built": time.strftime("%Y-%m-%d"), "keys": keys}
    (AUDIO / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False) + "\n", encoding="utf-8")
    for loc in LOCALES:
        print(f"{loc}: {len(keys.get(loc, []))} of {len(used[loc])} clips present")
    print(f"{made} clips added now, in {AUDIO.relative_to(REPO)}.")
    if report:
        OUT.mkdir(parents=True, exist_ok=True)
        (OUT / "report.txt").write_text("\n".join(report) + "\n", encoding="utf-8")
        print(f"{len(report)} problem(s), see {OUT / 'report.txt'}:\n  " + "\n  ".join(report[:10]))


def loudness(f: Path) -> float:
    err = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(f), "-af", "volumedetect", "-f", "null", "-"], capture_output=True, text=True).stderr
    m = re.search(r"mean_volume: (-?[\d.]+) dB", err)
    return float(m.group(1)) if m else -99.0


def import_pieces(index: dict, src_dir: Path, voice: str) -> None:
    """Copy clips that were already cut elsewhere (e.g. catalogue_voice/pieces/<key>.mp3) into the app.

    Keys are hashes of locale + text, so a clip's file name says which sentence piece or word it is.
    Each clip must decode, last at least 0.15 s and not be near-silent. If the folder's overrides.json lists
    `_regenerate` line ids, clips cut only from those recordings (per jobs.json) are left out."""
    for tool in ("ffmpeg", "ffprobe"):
        if not shutil.which(tool):
            sys.exit(f"{tool} not found on PATH.")
    pieces = src_dir / "pieces" if (src_dir / "pieces").is_dir() else src_dir
    bad_lines: set[str] = set()
    if (src_dir / "overrides.json").exists():
        bad_lines = set(json.loads((src_dir / "overrides.json").read_text(encoding="utf-8")).get("_regenerate", []))
    sources: dict[str, set[str]] = {}
    if bad_lines and (src_dir / "jobs.json").exists():
        for b in json.loads((src_dir / "jobs.json").read_text(encoding="utf-8")).get("bases", []):
            for p in b["pieces"]:
                sources.setdefault(p["key"], set()).add(b["id"])
    loc_of = {}
    for loc in LOCALES:
        for f in frames(index, loc):
            for p in f["pieces"]:
                loc_of[p["key"]] = loc
        for w in word_list(index, loc):
            loc_of[w["key"]] = loc
    report, made, locs = [], 0, set()
    for f in sorted(pieces.glob("*.mp3")):
        k = f.stem
        if k not in loc_of:
            report.append(f"{k}: not in the current voice index; skipped")
            continue
        if sources.get(k) and sources[k] <= bad_lines:
            report.append(f"{k}: cut from {sorted(sources[k])}, marked _regenerate; skipped")
            continue
        try:
            d = duration(f)
        except (subprocess.CalledProcessError, ValueError):
            report.append(f"{k}: does not decode; skipped")
            continue
        if d < 0.15 or loudness(f) < -40:
            report.append(f"{k}: too short or near-silent ({d:.2f} s); skipped")
            continue
        dest = AUDIO / loc_of[k] / f"{k}.mp3"
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(f, dest)
        made += 1
        locs.add(loc_of[k])
    write_manifest(index, made, report, "import", {l: voice for l in sorted(locs)}, None)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--index", action="store_true", help="rebuild frontend/src/voice/voice-index.json")
    ap.add_argument("--check", action="store_true", help="exit 1 if voice-index.json is out of date")
    ap.add_argument("--sheet", action="store_true", help="write out/recording-sheet.md and print the character count")
    ap.add_argument("--generate", action="store_true", help="make missing clips with ElevenLabs")
    ap.add_argument("--fake", action="store_true", help="with --generate: beeps instead of ElevenLabs")
    ap.add_argument("--recordings", type=Path, help="make missing clips from human recordings in this folder")
    ap.add_argument("--fresh", action="store_true", help="delete existing clips first")
    ap.add_argument("--import", dest="import_dir", type=Path, help="copy already-cut clips named <key>.mp3 from this folder")
    ap.add_argument("--voice", default="imported", help="with --import: voice name recorded in the manifest")
    a = ap.parse_args()
    index = build_index()
    for msg in sorted(SKIPPED):
        print(f"warning: not voiced (device voice): {msg}", file=sys.stderr)
    if a.check:
        ok = INDEX.exists() and INDEX.read_text(encoding="utf-8") == index_text(index)
        print("voice index up to date" if ok else "voice index OUT OF DATE: run build_voice.py --index")
        if (AUDIO / "manifest.json").exists():  # every clip the app is told about must be on disk
            listed = json.loads((AUDIO / "manifest.json").read_text(encoding="utf-8")).get("keys", {})
            missing = [f"{l}/{k}.mp3" for l, ks in listed.items() for k in ks if not (AUDIO / l / f"{k}.mp3").exists()]
            print(f"audio manifest: {sum(map(len, listed.values()))} clips listed, {len(missing)} missing" + (f": {missing[:5]}" if missing else ""))
            ok = ok and not missing
        sys.exit(0 if ok else 1)
    if a.index or a.generate or a.recordings:
        INDEX.write_text(index_text(index), encoding="utf-8")
        print(f"wrote {INDEX.relative_to(REPO)}: " + ", ".join(f"{l} {len(index['lines'][l])} lines" for l in LOCALES))
    if a.sheet:
        OUT.mkdir(parents=True, exist_ok=True)
        text = sheet(index)
        (OUT / "recording-sheet.md").write_text(text, encoding="utf-8")
        print(text.splitlines()[3].strip(), f"→ {OUT / 'recording-sheet.md'}")
    if a.generate or a.recordings:
        produce(index, "recordings" if a.recordings else "fake" if a.fake else "eleven", a.recordings, a.fresh)
    if a.import_dir:
        if a.fresh and AUDIO.exists():
            shutil.rmtree(AUDIO)
        import_pieces(index, a.import_dir, a.voice)
    if not any([a.index, a.sheet, a.generate, a.recordings, a.import_dir]):
        ap.print_help()


if __name__ == "__main__":
    main()
