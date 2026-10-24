# STATE

Read this file before any work in this repository and update it in the same PR as the work.
The PR evidence check fails when STATE.md exists and a PR neither updates it nor says
"no change" with a reason. Keep it under 60 lines; facts only, each with a date or SHA.

## Repository

- Type and lifecycle: hardware, active
- Readiness: R0 (evidence: Repository quality run 40087607773 on main b4d7157, 2026-10-24;
  no hardware check runs on main yet)
- Owner role: platform-lead (maintainers.yaml); code owners in .github/CODEOWNERS
- Verification: `python3 tools/ci/check_hw_repo.py --root .` (in PR #34, not on main);
  Repository quality last PASS on main at b4d7157 (2026-10-24)
- Harness rollout: step (a) in this PR; steps (b) to (e) not started (rollout/README.md)

## Current work

| Work package | Branch or PR | Status | Next step |
|---|---|---|---|
| E-01 safety chain and power baseline | #27 e01-safety-power | draft | platform-lead review |
| ZLTECH B2 double-shaft drawing | #28 nightly/2026-10-16-zltech-b2-double-shaft-drawing | draft | owner review |
| P-03 rev19.4 reconciliation | #29 audit/p03-rev19-4-hardware-docs-2026-10-16 | draft | owner review |
| Hardware repository checks | #34 ci/hardware-checks | draft | review, then merge |
| Split SW17 model ZIP | issue #33 | open | upload the missing archive parts |
| Shared rules v2, STATE.md | governance/agent-rules-state (this PR) | draft | owner adopt/adapt/reject |

## Decisions this repository implements

BASE-CONTROLLER-IO, BASE-CONTROLLER-GATES, SAFETY-CHAIN-IO, NAV-LIDAR, DRIVETRAIN,
RS485-NOT-IN-2-0, CAMERAS, CHARGING, ESTOP-SCOPE, FRAMES-REP105, BOM-ISSUE-IN-FORCE, COMPUTE
(register openAMRobot/.github decisions.yaml at 1c3f516, 2026-10-24).

## Known gaps

- No KiCad PCB sources yet: `electrical/pcb/` holds only .gitkeep (main b4d7157, 2026-10-24).
- No machine-readable controller I/O contract under `interfaces/electrical/` yet (2026-10-24).
- Local .github/PULL_REQUEST_TEMPLATE.md overrides the organization template; alignment
  (rollout step (a)) left to the owner (2026-10-24).
- SW17 model ZIP is one part of a split archive, tracked in #33.

## Not verified

- No CAD, wiring or BOM content has been checked against the physical robot (2026-10-24).
- Hardware checks of PR #34 have not run on main (2026-10-24).
