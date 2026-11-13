"""Build a pre-cleanup inventory without changing original project files."""
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'docs/handoff-20261113'
OUT.mkdir(exist_ok=True)

# Preserve authored documentation/source buried inside the excluded evidence ZIP.
# Keep their historical paths beneath a clearly labelled archive snapshot.
archive_decisions = []
with zipfile.ZipFile(ROOT / 'docs/VALIDATION_ARTIFACTS.zip') as z:
    for info in z.infolist():
        rel = Path(info.filename)
        safe = (rel.suffix.lower() in ('.md', '.py', '.json', '.ps1') or rel.name == 'installed_requirements.txt') and not rel.name.startswith('power_sakha_')
        if info.is_dir():
            continue
        destination = 'archive-snapshot/' + info.filename if safe else None
        archive_decisions.append({'member':info.filename,'published_copy':destination,'reason':None if safe else 'Scientific/model payload, execution log, environment license or third-party reference; retained in separately transferred archive'})
        if safe:
            if rel.is_absolute() or '..' in rel.parts:
                raise ValueError('Unsafe archive path')
            target = ROOT / destination
            target.parent.mkdir(parents=True, exist_ok=True)
            content = z.read(info)
            if target.exists() and target.read_bytes() != content:
                raise ValueError('Refusing to overwrite archive snapshot')
            if not target.exists():
                target.write_bytes(content)
(OUT / 'ARCHIVE_DISPOSITION.json').write_text(json.dumps(archive_decisions, indent=2)+'\n', encoding='utf-8')

def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT).decode().splitlines()

def sha(p):
    with p.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

tracked = set(git('ls-files'))
untracked = set(git('ls-files', '--others', '--exclude-standard'))
ignored = set(git('ls-files', '--others', '--ignored', '--exclude-standard'))
paths = sorted(tracked | untracked | ignored)
rows = []
for name in paths:
    p = ROOT / name
    if not p.is_file() or name.startswith('docs/handoff-20261113/'):
        continue
    parts = p.relative_to(ROOT).parts
    reason = None
    if any(x in parts for x in ('.venv', 'node_modules', 'uv-cache', '__pycache__', '.pytest_cache')):
        reason = 'Environment/dependency/runtime cache; recreate with dependency manifests'
    elif p.suffix.lower() in ('.zip', '.safetensors', '.pt', '.pth', '.ckpt', '.onnx', '.csv') or p.name.startswith('power_sakha_'):
        reason = 'Scientific data/model payload; transfer exact bytes separately (see ARTIFACT_TRANSFER.md)'
    elif p.suffix.lower() in ('.log', '.patch') or p.name in ('initial_status.txt',):
        reason = 'Generated local execution/working-tree diagnostic; retained locally'
    elif p.name.startswith('.env') and not p.name.endswith('.example'):
        reason = 'Potential local secrets; never publish'
    rows.append({'path': name, 'bytes': p.stat().st_size, 'sha256': sha(p),
                 'original_git_state': 'tracked' if name in tracked else 'ignored' if name in ignored else 'untracked',
                 'decision': 'exclude' if reason else 'publish', 'reason': reason})
(OUT / 'LOCAL_INVENTORY.json').write_text(json.dumps(rows, indent=2)+'\n', encoding='utf-8')
members = []
archive = ROOT / 'docs/VALIDATION_ARTIFACTS.zip'
with zipfile.ZipFile(archive) as z:
    for info in z.infolist():
        if not info.is_dir():
            with z.open(info) as f:
                digest = hashlib.file_digest(f, 'sha256').hexdigest()
            members.append({'archive':'docs/VALIDATION_ARTIFACTS.zip','member':info.filename,'bytes':info.file_size,'sha256':digest})
(OUT / 'ARCHIVE_MEMBERS.json').write_text(json.dumps(members, indent=2)+'\n', encoding='utf-8')
for label, subset in [('MARKDOWN_FILES.txt',[r['path'] for r in rows if r['decision']=='publish' and r['path'].endswith('.md')]),('SOURCE_CONFIG_TEST_ASSETS.txt',[r['path'] for r in rows if r['decision']=='publish' and not r['path'].endswith('.md') and not r['path'].endswith('.gitkeep')])]:
    (OUT/label).write_text('\n'.join(subset)+'\n',encoding='utf-8')
print(json.dumps({'publish':sum(r['decision']=='publish' for r in rows),'excluded':sum(r['decision']=='exclude' for r in rows),'archive_members':len(members)}))
