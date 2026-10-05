"""One-command, isolated study. No hardware or production imports."""
import argparse
import hashlib
import json
import platform
from pathlib import Path
import subprocess
import sys
import unittest

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[1]
sys.path.insert(0,str(ROOT))
BASELINE='d385b055bef23af3b01960f7b2c113c2e683fe59'
TAG='tark-software-evidence-r1-2026-09-28'


def write_json(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n',encoding='utf-8',newline='\n')


def baseline_gate():
    def git(*args):return subprocess.check_output(['git',*args],cwd=REPO,text=True,timeout=20).strip()
    if git('rev-parse',TAG+'^{}')!=BASELINE:raise ValueError('R1 tag moved')
    subprocess.run(['git','merge-base','--is-ancestor',BASELINE,'HEAD'],cwd=REPO,check=True,timeout=20)
    changed=git('diff',BASELINE,'--name-only').splitlines()
    allowed_docs=set(__import__('src.reports',fromlist=['DOCS']).DOCS)
    if any(not (p.startswith('studies/sih26007_simulation/') or p in allowed_docs) for p in changed):
        raise ValueError('non-study tracked files changed relative to R1')
    return git('branch','--show-current')


def main(argv=None):
    parser=argparse.ArgumentParser();parser.add_argument('--verify',action='store_true');args=parser.parse_args(argv)
    try:
        branch=baseline_gate()
        from src.verify import verify_numbers,verify_hashes,verify_summary
        if args.verify:
            result=verify_numbers(ROOT);result['headline_checks']=verify_summary(ROOT);result['hashed_files']=verify_hashes(ROOT,REPO)
            print(json.dumps(result));return 0
        from src.experiments import run
        from src.plots import render
        from src.reports import generate,DOCS
        d,t,tables=run(ROOT,REPO);figures=render(ROOT)
        result=verify_numbers(ROOT)
        suite=unittest.defaultTestLoader.discover(str(ROOT/'tests'),pattern='test_*.py')
        tests=unittest.TextTestRunner(verbosity=1).run(suite)
        if not tests.wasSuccessful():raise ValueError('study tests failed')
        result['tests_run']=tests.testsRun
        write_json(ROOT/'results/numerical_verification.json',result)
        generate(ROOT,REPO,d,t,result)
        result['headline_checks']=verify_summary(ROOT)
        import numpy,matplotlib
        inventory=[p.relative_to(ROOT).as_posix() for p in sorted(ROOT.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.name not in ['manifest.json','hashes.json']]
        manifest={'study_name':'SIH26007 requirement-driven engineering simulation','date':d['study_date'],
            'git_baseline':BASELINE,'branch':branch,'r1_release':TAG,'official_ps':'SIH26007',
            'source_files':json.loads((ROOT/'sources/source_inventory.json').read_text()),
            'equations':['Dstop=v*t+v^2/(2*a)+m','Rreq=Dstop+u','margin=R-Rreq','vmax=max(0,positive root of Rreq=R)','cycle=fixed+nonfog+fog*vdesired/vtravel+dwell_if_halted'],
            'parameter_registry_sha256':hashlib.sha256((ROOT/'inputs/parameter_registry.csv').read_bytes()).hexdigest(),
            'seed':d['seed'],'sample_counts':d['uncertainty']['counts'],'simulation_ids':[f'SIM-{i:02d}' for i in range(1,11)],
            'python':platform.python_version(),'libraries':{'numpy':numpy.__version__,'matplotlib':matplotlib.__version__},
            'output_inventory':inventory,'repository_reports':DOCS,'hardware_access':False,'physical_validation':False,'production_code_modified':False,'traction':'DISABLED_PHASE_1'}
        write_json(ROOT/'manifest.json',manifest)
        files=[p for p in ROOT.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='hashes.json']+[REPO/p for p in DOCS]
        write_json(ROOT/'hashes.json',{p.relative_to(REPO).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files)})
        result['hashed_files']=verify_hashes(ROOT,REPO);print(json.dumps(result));return 0
    except (ValueError,OSError,subprocess.SubprocessError,AssertionError,KeyError,TypeError) as exc:
        print(f'STUDY GATE FAILED: {exc}',file=sys.stderr);return 1


if __name__=='__main__':raise SystemExit(main())
