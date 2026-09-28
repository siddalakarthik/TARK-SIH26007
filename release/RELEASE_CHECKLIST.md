# R1 release checklist

TARK PHASE-1 SOFTWARE EVIDENCE RELEASE R1.
Final commit/tag are permitted only after all software/document gates pass.
An absent release tag means the release has not been issued.

| Item | Status | Evidence / scope |
|---|---|---|
| Exact source baseline | PASS | bf87304ab2080452d5446fb4b6bbfcb945cf74ea; Prompt-1/2 ancestry checked |
| Release branch | PASS | tark/project-convergence-release |
| Human/machine manifest | PASS | TARK_RELEASE_MANIFEST.md / JSON |
| Claim matrix | PASS | 60 claims with evidence and wording limits |
| Maturity matrix | PASS | Subsystems, not overall percentage |
| Protocol V2 authority | PASS | V2 current; retained V1 filename historical |
| Prompt-1 evidence | PASS | Current 65 integrity tests; original report retained |
| Prompt-2 evidence | PASS | Current 68 protocol and 35 replay tests; original report retained |
| Prompt-3 package | PASS | 20 scenarios/150 reps; inventory/source verification |
| Test record | PASS | 322 backend, 39 frontend, types/build, fresh strict C fixture |
| Dashboard terminology | PASS | Source inspected; truthful labels retained; no UI edit |
| Public-demo record | HISTORICAL | Recorded simulation/monitoring URL and captures |
| Current public availability/revision | PENDING | No network check or R1 deployment authorized |
| PPT | PASS | Patch sheet route; three six-slide variants inspected |
| PPT binary correction | PENDING | Binary not modified or marked corrected |
| Film | PASS | Narration/captions/storyboard/metadata audited |
| Film binary revision | NOT APPLICABLE | Explicitly forbidden in this pass |
| Electrical package | HOLD | Controlled design only; no energization/fabrication |
| HOLD register | HOLD | 27 retained HOLD/restriction entries; none closed |
| Physical validation/commissioning | PENDING | No hardware access or physical claim |
| BOM procurement | HOLD | Exact parts/ratings/quotes need controlled review |
| Known limitations | PASS | Provisional D_env, speed, TTC/WARN, research/physical limits explicit |
| Next-phase handoff | PASS | Thirteen gated categories; no work performed |
| Current links/claim search/file scope | PASS | Final checked inventory in claim-search audit; production diff empty |
| Old freeze tag unchanged | PASS | Object 94b149a50d77c45d3a8b962781c503a1055a0c8f |
| Push/deployment | NOT APPLICABLE | Not authorized or performed |

Issuance is resolved by the local Git objects, not a self-referential hash:
exactly one commit named `CONVERGE PROJECT CLAIMS AND SOFTWARE EVIDENCE RELEASE`,
followed by annotated tag `tark-software-evidence-r1-2026-09-28`. Verify with
`git show` / `git rev-parse`; absent/mismatched objects mean NOT RELEASED.
No PASS row implies mine certification or physical verification.
