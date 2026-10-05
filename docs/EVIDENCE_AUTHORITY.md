# Evidence and release authority

## Authority order

1. [Release manifest](TARK_RELEASE_MANIFEST.md): identity and declared scope.
2. Source at the manifest's exact software commit: implemented behavior.
3. Tests and [Prompt-3 artifacts](../evidence/prompt3/README.md): demonstrated
   software properties, not unrestricted correctness.
4. [Protocol V2](ESP32_PROTOCOL_V2.md): current Pi↔ESP32 software contract.
5. [Controlled five-sheet electrical reference](../release/references/electrical/TARK_SIH26007_MASTER_ELECTRICAL_SCHEMATIC_SET.pdf):
   intended wiring within HOLDs; no energization/fabrication release.
6. Exact purchased component datasheets: actual component limits. A conflict
   with the design is a HOLD requiring review, never permission to improvise.
7. Dossier/architecture/manual: explanatory intent subject to current sources.
8. PPT, film and website: communication, not engineering overrides.

## Identity without a self-referential hash

The manifest pins software to `bf87304ab2080452d5446fb4b6bbfcb945cf74ea`.
Prompt 4 changes documentation/release control only. Its own future Git object
ID cannot be embedded in itself without changing that ID. The machine manifest
specifies the exact source commit and a release-commit resolver:
the new annotated tag, dereferenced with `^{commit}`. The tag is created only
after the single release commit and successful gates. It is not the historical
freeze tag and will not be pushed in this pass. Final handoff reports the
resolved literal release commit; an absent tag means the release gate is open.

## Prompt-3 provenance

The original manifest records pre-commit HEAD `96bf72b...`, dirty=true and
the source inventory used during generation. Commit `bf87304...` contains those
same verified source bytes and the evidence bundle. This is not rewritten to
pretend the files were generated from their own future commit. Source hashes
normalize CRLF to LF; artifact hashes identify exact bytes. The SHA-256 of
`evidence/prompt3/hashes.json` fingerprints that inventory (which excludes
itself). Hashes detect changes; they are **not digital signatures** or proof
against deliberate wholesale replacement.

External evidence is labelled TEST_FIXTURE even where a recording's internal
REAL source denotes the production input boundary. REAL is not physical
verification. No physical opener was reached. The endpoint simulator is Python;
separate fresh C host tests exercise firmware software, not an ESP32 board.

Replay MATCH establishes deterministic reconstruction for defined fields and
scenarios, not universal correctness. Protocol interoperability is not motor,
watchdog, E-stop, latency, braking or mine validation. Numerical research packages
are separate experiments; their policies are not production-code evidence.

## Reproduction

From the installed repository Python environment, first clear inherited
nonempty `TARK_*` settings; permit only `TARK_DATABASE_PATH=:memory:` during
the test process. Do not configure physical device paths. Run:

```text
python scripts/run_evidence_harness.py --verify evidence/prompt3
python -B -m pytest -q -p no:cacheprovider --tb=short
```

The existing `test_protocol_correctness.py::host` fixture compiles fresh C
executables with `-std=c11 -Wall -Wextra -Werror` and runs protocol/service and
cross-language cases. Report OS application-control denials as denials, never
as passed tests; do not disable security controls. From `frontend`, run
`pnpm test`, `pnpm run lint:types`, `pnpm run build`.

For a separately authorized new evidence run, use the CLI's `--output` with
a new directory. It refuses overwrite. This pass verifies the supplied bundle
without regenerating it. Any production change requires new evidence review.
