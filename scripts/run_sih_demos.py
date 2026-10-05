"""Run exactly three deterministic R3 SIH demos without device access."""
import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'backend'))
from app.r3.sih_demos import DEMOS, run_demo


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scenario', choices=[*DEMOS, 'all'], default='all')
    parser.add_argument('--output', type=Path, default=ROOT.parent / 'work' / 'sih_preselection')
    args = parser.parse_args()
    names = list(DEMOS) if args.scenario == 'all' else [args.scenario]
    if any((args.output / DEMOS[name][0]).exists() for name in names):
        parser.error('demo output exists; choose a fresh --output directory (never overwritten)')
    passed = True
    for name in names:
        output = args.output / DEMOS[name][0]
        summary = run_demo(name, output)
        print(f'\n{summary["demo_id"]} — SIMULATION / SYNTHETIC EVIDENCE')
        for stage in summary['stages']:
            print(f'  {stage["stage"]:24} {stage["observed"]:8} {stage["reason"]}')
        print(f'  {summary["ticks"]} persisted ticks; R3 replay={summary["replay"]["result"]}; qualification={summary["qualification_replay"]["result"]}; isolated={summary["replay_isolated"]}')
        print(f'  Evidence: {output.resolve()}')
        passed &= summary['passed']
    print('\nNo hardware accessed. No motion authority. Traction DISABLED_PHASE_1.')
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
