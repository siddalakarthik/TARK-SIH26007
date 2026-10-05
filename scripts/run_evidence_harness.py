"""Run from repository root using the existing Python project environment."""
from pathlib import Path
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/"backend"))


def main():
    parser = argparse.ArgumentParser(description="Offline deterministic TARK evidence; no hardware access")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--output", type=Path, default=ROOT/"evidence/prompt3", help="fresh output directory; never overwritten")
    group.add_argument("--verify", type=Path, help="verify existing artifact hashes, semantics and replay")
    args = parser.parse_args()
    try:
        from app.evidence.runner import isolated_environment
        from app.evidence.artifacts import build_bundle, verify_bundle
        with isolated_environment():
            result = verify_bundle(args.verify) if args.verify else build_bundle(args.output)
        print(json.dumps(result, sort_keys=True))
        return 0
    except Exception as error:
        # Do not print environment values/credentials or platform-specific paths.
        print(f"EVIDENCE FAILED: {type(error).__name__}: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
