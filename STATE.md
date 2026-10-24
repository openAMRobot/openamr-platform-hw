# STATE

Read this file before any work in this repository and update it in the same PR as the work.
The PR evidence check fails when STATE.md exists and a PR neither updates it nor says
"no change" with a reason. Keep it under 60 lines; facts only, each with a date or SHA.

## Repository

- Type and lifecycle: hardware, active
- Readiness: R0 (evidence: Hardware checks run 40095253918 on main eaac115, 2026-10-24;
  layer 1 only, no nightly yet)
- Owner role: platform-lead (maintainers.yaml); code owners in .github/CODEOWNERS
- Verification: `python3 -m unittest discover -s tests -v` and `python3 tools/ci/check_hw_repo.py
  --root .`; Hardware checks last PASS on main at eaac115 (#34 merged, 2026-10-24)
- Harness rollout: step (a) in this PR; steps (b) to (e) not started (rollout/README.md)

## Current work

| Work package | Branch or PR | Status | Next step |
|---|---|---|---|
| E-01 safety chain and power baseline | #27 e01-safety-power | draft | platform-lead review |
| ZLTECH B2 double-shaft drawing | #28 nightly/2026-10-16-zltech-b2-double-shaft-drawing | draft | owner review |
| P-03 rev19.4 reconciliation | #29 audit/p03-rev19-4-hardware-docs-2026-10-16 | draft | owner review |
| Shared rules v2, STATE.md | #35 governance/agent-rules-state (this PR) | draft | owner adopt/adapt/reject |
| Layer 1: electrical contract, BOM, PCB checks | #37 ci/electrical-contract | draft | owner review of contract 0.1.0 |
| Layer 2: Hardware nightly, ci-evidence.json | #38 ci/nightly-evidence (on #37) | draft | retarget to main after #37 |
| Split SW17 model ZIP | issue #33 | open | upload the missing archive parts |
| BOM quantities "1 set", "1–2" | issue #36 | open | BOM owner gives counts |

## Decisions this repository implements

BASE-CONTROLLER-IO, BASE-CONTROLLER-GATES, SAFETY-CHAIN-IO, NAV-LIDAR, DRIVETRAIN,
RS485-NOT-IN-2-0, CAMERAS, CHARGING, ESTOP-SCOPE, FRAMES-REP105, BOM-ISSUE-IN-FORCE, COMPUTE
(register openAMRobot/.github decisions.yaml at 1c3f516, 2026-10-24).

## Known gaps

- No KiCad PCB sources yet: `electrical/pcb/` holds only .gitkeep; the PCB job of #37 and #38
  reports "NOT RUN: no KiCad projects" (2026-10-24).
- Controller I/O contract 0.1.0 (#37) is a PROPOSAL; FDCAN AFs unchecked, item 22 pins tbd.
- Local .github/PULL_REQUEST_TEMPLATE.md overrides the organization template; alignment
  (rollout step (a)) left to the owner (2026-10-24).
- SW17 model ZIP is one part of a split archive, tracked in #33.

## Not verified

- No CAD, wiring or BOM content has been checked against the physical robot (2026-10-24).
- Hardware nightly (#38) has not run: schedule and dispatch need it on main (2026-10-24).
