# R1 claim-search and release-gate audit

Date: 2026-09-28. TARK PHASE-1 SOFTWARE EVIDENCE RELEASE R1.
Audit only; no runtime/policy redesign.

## Search coverage

[Machine ledger](../release/CLAIM_SEARCH_INVENTORY.json): 286 repository text
files scanned, 639 matching lines in 116 files. Each occurrence records path,
line, matched terms, exact text, disposition and reason. Post-correction:
408 KEEP and 231 MARK HISTORICAL. These are search-line counts, not the
60 distinct claims in the claim matrix.

Scope: tracked source/configuration/tests/docs and new release/reference text.
Ignored dependencies, generated build/cache/runtime files and binary payloads
are excluded; supplied PPTX/DOCX/film content has its separate extraction/audit.
This audit and its generated ledger are excluded from the search to avoid
recursive matches.

Case-insensitive searches cover Protocol V1, V1, the old spec filename,
fully validated, physical validation, complete system, all gaps closed, no gaps,
final software, software complete/completely finished, communication completely
closed, all software verified, no further software work, production ready,
mine ready/certified, collision prevention, guarantee, autonomous, RTK,
centimeter/centimetre, EKF, fusion, TTC, WARN, watchdog, E-stop, stopping
distance, fog tested, physical prototype, test counts and 97/25/252 passed.
API `/api/v1`, recording schema V1 and intentionally rejected legacy values
are not renamed as though they were current wire-protocol authority.

## Reviewed corrections and retained evidence

| Area / files | Before | Disposition now |
|---|---|---|
| README | Deployment-ready classification, missing URL/remote, old closure authority | UPDATE to R1 and recorded demo; no new external verification |
| Protocol docs, firmware README/implementation | Current V2 content under V1 filename | UPDATE current links to V2; MARK V1 file historical, retain body |
| 19 old reports/freeze records | Stage-specific blanket completion and old counts | MARK HISTORICAL with visible notice; do not rewrite old test results |
| Prompt-1/2 reports | Deferred-stage work and stage-specific counts could read as current | QUALIFY with scoped-evidence notice; source histories preserved |
| TEST_REPORT | 252 presented as current | UPDATE current 322/39 and dated final run; preserve older sections |
| ESP32 integration/hardware interface | V1 and ambiguous “V2” wiring/manual reference | UPDATE V2 software link; explicit five-sheet physical design authority |
| Firmware BUILD | Incomplete old one-line host link command | UPDATE documentation to existing tested pytest host fixture; no script/source change |
| Firmware fault matrix | Disconnect software/physical integration conflated | QUALIFY portable software pass versus physical USB binding pending |
| Simulation guide | Deeper replay fixes still deferred; ambiguous REAL_HARDWARE mode | UPDATE implemented format-2 semantics and actual mode names |
| Fault matrix | Storage failure “not injected yet”; TTC looked production-active | UPDATE evidence negative control; QUALIFY TTC as helper only |
| IMU/thermal guides | “Dormant boundary” without runtime-bootstrap scope | QUALIFY configured/identity-gated concrete lifecycle and mock evidence |
| UI guide | Current/permitted speed and TTC availability unclear in prose | QUALIFY measured UNAVAILABLE versus command zero; NOT COMPUTED |
| Public deployment | Account/hostname unavailable described as present condition | UPDATE historical demo record, keep simulation/monitoring; no R1 deployment claim |
| Hardware checklist / next-phase | Older schematic/manual referenced without current HOLD authority | UPDATE five-sheet/HOLD links; no energization authority |
| .env.example | Decoder described as absent | UPDATE comment only; exact key/value sequence unchanged |
| Dossier/manual/architecture | V1, tracking/TTC/WARN, percentage maturity, old wiring reference | MARK HISTORICAL; section-by-section current corrections in supersession register |
| PPT | Production EKF/fusion/TTC, old counts, physical/watchdog implication | QUALIFY/CORRECT exact text in patch sheet only; all three six-slide variants reviewed |
| Film | Target identity, provisional envelope, TTC/UI/deployment age | QUALIFY/CORRECT specified narration lines only; unchanged binary |
| Research studies | Synthetic studies could be mistaken for deployed fusion/fog tests | KEEP as RESEARCH / SIMULATION STUDY with fingerprinted provenance |
| Current UI source | UNAVAILABLE / NOT COMPUTED / source and parameter labels already present | KEEP code untouched; no behavior change or extra frontend claim |
| Prompt-3 evidence/spec | Already scoped, provenance-aware and immutable | KEEP unchanged; verification PASS |
| Current protocol V1 mentions | Legacy rejection/compatibility explanation | KEEP; no active V1 authority |
| REAL / NORMAL | Endpoint semantics / modeled decision state | QUALIFY in current docs; neither physical verification nor certification |

Current-facing remaining positive software assertions were checked against
the cited source/tests. Forbidden examples, negative statements and historical
quotes remain intentionally visible. Search matches alone are not evidence of
an overclaim. Source/test vocabulary is not replaced for prose aesthetics.

## Reference/link and scope checks

Current Markdown relative links resolve. Current navigation contains no
developer-specific absolute filesystem dependency. The one original
Prompt-2 OS-denial path remains in a clearly historical report; preserved raw
reference metadata may also contain historical provenance paths.
No external link availability was checked.

Read-only electrical/dossier copies are byte-identical to their supplied
sources. The film MP4 hash matches its recorded QA identity; no audiovisual
edit or new render is claimed. All 19 reference hashes verify with the stated
text-normalization/binary-byte rules. Description word counts: 25 / 75 / 175.
Judge Q&A: 34 questions. Release report: 20 required sections.

Diff check: production application, frontend source, firmware C/H/tests,
runtime/configuration values, scripts, dependencies, deployment, protocol
vectors and Prompt-3 evidence unchanged. .env.example differs only in comments.
All new files are controlled docs, release metadata or read-only reference
copies/extractions. No unrelated user changes were present in the clean
starting tree.

## Final executed gates

First: Prompt-3 independent verification PASS — 20 scenarios, 150 repetitions,
85 artifacts, 971433 inventoried bytes; observer equivalence MATCH.

Final September 28 run:

| Gate | Actual outcome |
|---|---|
| Full backend | 322 passed, no failures/skips, 70.90 s |
| Protocol/interoperability | 68 included tests pass |
| Replay | 35 included tests pass |
| Prompt-1 integrity | 65 included tests pass |
| Harness | 70 included tests pass |
| Fresh strict C fixture | Protocol/shared-vector executable, service/supervisor executable and C/Python interop compile/run PASS |
| Frontend | 39 passed / 9 files, 6.57 s |
| TypeScript | PASS |
| Vite production build | PASS, 5.63 s |
| Safety | DISABLED_PHASE_1; live permitted/left/right zero; no hardware access |

Exact runners/environment are in [TEST_REPORT](TEST_REPORT.md) and
[EVIDENCE_AUTHORITY](EVIDENCE_AUTHORITY.md). No test is removed, weakened or
skipped. Existing upstream deprecations and 816.49 kB lazy-map chunk advisory
remain disclosed. The historical shell-helper application-control denial is
not relabelled a pass; the unchanged canonical fresh fixture ran successfully.

## Issuance controls

Starting HEAD bf87304ab2080452d5446fb4b6bbfcb945cf74ea and Prompt-1/2 ancestry
verified. Branch tark/project-convergence-release. Historical freeze tag object
94b149a50d77c45d3a8b962781c503a1055a0c8f remains unchanged.

Exactly one authorized local release commit follows these gates:
CONVERGE PROJECT CLAIMS AND SOFTWARE EVIDENCE RELEASE.
A new annotated local tag identifies that commit; the final handoff verifies
its literal hash, clean tree and tag. No push/deployment is performed.
This is software-evidence release control, not approval to energize hardware.
