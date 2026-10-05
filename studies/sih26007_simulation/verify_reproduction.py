"""Regenerate twice and compare deterministic numerical, figure and report bytes."""
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import run_all
from src.reports import DOCS
from src.verify import verify_hashes


def selected():
    root=run_all.ROOT
    files=[p for p in root.rglob('*') if p.is_file() and p.suffix in ['.csv','.png','.svg']]
    files += [root/'results/final_simulation_summary.json']+[run_all.REPO/p for p in DOCS]
    return {p.relative_to(run_all.REPO).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files)}


def main():
    if run_all.main([]):return 1
    first=selected()
    if run_all.main([]):return 1
    second=selected()
    if first!=second:raise ValueError('repeat-run artifacts differ')
    root=run_all.ROOT
    run_all.write_json(root/'results/reproduction_check.json',{'result':'PASS','consecutive_generations':2,
        'byte_identical_selected_artifacts':len(first),'scope':'CSV tables/master/registry/fault metrics; PNG/SVG figures; eight reports and final numerical summary',
        'selected_sha256':second,'note':'Exact library versions recorded in manifest; this does not establish cross-platform identical font rendering'})
    m=json.loads((root/'manifest.json').read_text());m['output_inventory']=sorted(set(m['output_inventory']+['results/reproduction_check.json']))
    run_all.write_json(root/'manifest.json',m)
    files=[p for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='hashes.json']+[run_all.REPO/p for p in DOCS]
    run_all.write_json(root/'hashes.json',{p.relative_to(run_all.REPO).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files)})
    print(json.dumps({'repeat_run':'PASS','byte_identical_artifacts':len(first),'hashed_files':verify_hashes(root,run_all.REPO)}))
    return 0


if __name__=='__main__':raise SystemExit(main())
