"""Verify selected local files against a Git index/commit; regenerate inventories."""
import json
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parent
out = root / 'docs/handoff-20261113'
ref = sys.argv[1] if len(sys.argv) > 1 else ':'
def run(*args):
    return subprocess.check_output(['git', *args], cwd=root)
names = set(run('ls-files').decode().splitlines()) if ref == ':' else set(run('ls-tree', '-r', '--name-only', ref).decode().splitlines())
if ref == ':':
    names.add('verify_handoff.py')
    names.update(p.relative_to(root).as_posix() for p in out.iterdir() if p.is_file())
    for filename, selected in [('MARKDOWN_FILES.txt', sorted(n for n in names if n.endswith('.md'))), ('SOURCE_CONFIG_TEST_ASSETS.txt', sorted(n for n in names if not n.endswith('.md') and not n.endswith('.gitkeep')))]:
        (out / filename).write_text('\n'.join(selected)+'\n',encoding='utf-8')
    print('Inventories generated; stage them before commit verification.')
else:
    rows = json.loads((out / 'LOCAL_INVENTORY.json').read_text())
    missing = [r['path'] for r in rows if r['decision']=='publish' and r['path'] not in names]
    unexpected = [r['path'] for r in rows if r['decision']=='exclude' and r['path'] in names]
    mismatches = []
    for name in sorted(names):
        expected = run('hash-object', '--path='+name, name).decode().strip()
        actual = run('rev-parse', ref+':'+name).decode().strip()
        if expected != actual:
            mismatches.append(name)
    for filename, selected in [('MARKDOWN_FILES.txt', sorted(n for n in names if n.endswith('.md'))), ('SOURCE_CONFIG_TEST_ASSETS.txt', sorted(n for n in names if not n.endswith('.md') and not n.endswith('.gitkeep')))]:
        assert (out/filename).read_text().splitlines() == selected, filename
    ml = sorted(n for n in names if n.startswith('docs/implementation/') and n.endswith('.md'))
    assert len(ml)==8, ml
    assert not missing and not unexpected and not mismatches, (missing, unexpected, mismatches)
    print(json.dumps({'ref':ref,'files':len(names),'markdown':sum(n.endswith('.md') for n in names),'source_config_test_assets':sum(not n.endswith(('.md','.gitkeep')) for n in names),'ml_handoffs':len(ml),'missing':missing,'excluded_published':unexpected,'content_mismatches':mismatches,'local_comparison':'Git clean filters applied (existing line-ending policy)'}))
