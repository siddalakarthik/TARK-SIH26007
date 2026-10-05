# Prompt-3 deterministic software evidence

TEST_FIXTURE; no hardware accessed, no physical validation. Traction DISABLED_PHASE_1.

From repository root, use `python scripts/run_evidence_harness.py --output <fresh-directory>`; verify with `python scripts/run_evidence_harness.py --verify <directory>`. Use the existing project environment. Unset inherited TARK_* configuration; only TARK_DATABASE_PATH=:memory: is permitted. No network, sensor devices or package installation is required.

Manifest fingerprints identify source/configuration/tool versions. Text source hashes normalize CRLF to LF; artifact hashes cover exact bytes and exports use LF. Runs contain all 150 repeat results; traces and replay contain one full representative per scenario. Replay exports retain UUIDs; logical traces omit event/storage UUIDs at named projections. Only top-level run_id, scenario_id and observer_reads are excluded from the logical digest. All controlled times, sessions, health, decisions, events, commands and sequences remain included. Observer reads have separate before/after authority checks.

A trace's decision is the LAST GENERATED decision. publication_available=false explicitly means it is not current evidence; clock-only fault steps deliberately show this distinction. Protocol snapshot fields are last-tick values; client/receiver/communication_health record current controlled time. wire_commands includes deliberately re-injected old frames; command_submissions counts actual production submit calls.

The replay-mode normalized queue retains the application's REAL boundary label internally; every input here is a TEST_FIXTURE, not real radar. The in-process receiver uses production Python protocol/supervision code. Fresh C host/interoperability regression is separately recorded in the report.

Hashes cover every artifact except hashes.json itself. They detect changes, not provenance against a party replacing the entire package. The verifier also checks semantics, expected outcomes and replay. Host durations are not WCET. Pre-commit source hashes avoid claiming a self-referential commit identity.
