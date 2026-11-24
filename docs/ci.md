# Continuous integration

OpenAMRobot CI has four layers:

- Pull request checks prove that each change is internally valid. Fast, deterministic, required before merge, no physical hardware.
- Nightly integration checks prove that the repositories still agree, across pinned commits.
- Hardware-in-the-loop checks prove that the real electronics behave as designed, on a controlled self-hosted bench runner.
- Release evidence proves which exact system was tested.

A passing check in this repository proves that files are well formed and consistent with each
other and with the decisions register. It never proves that a mechanical, electrical or safety
design is correct. SKIP or NOT RUN is never reported as PASS.

## Layer 1: pull request checks

Workflow `.github/workflows/hardware-checks.yml` ("Hardware checks"), on every pull request and on
pushes to `main`. GitHub-hosted runners only; no secrets and no hardware.

| Step | Command | Proves |
|---|---|---|
| Checker self-tests | `python -m unittest discover -s tests -v` | every checker fails on its fixtures; an empty suite fails |
| Repository files | `python tools/ci/check_hw_repo.py --root .` | links resolve; PDF, STEP, ZIP, STL and image files are complete; no LFS pointers; sizes; binary attributes; datasheet index |
| Electrical contract | `python tools/ci/check_electrical_contract.py --register <.github>/decisions.yaml --require-register` | `interfaces/electrical/base-controller-io.yaml` validates against its schema, uses no GPIO twice, puts no signal on a reserved pin, gives no AF to a not_required pin, gives an AF to every verified or proposed alternate-function pin, has four MB7060 and two TF-Luna, and agrees with the register entry BASE-CONTROLLER-IO |
| BOM | `python tools/ci/check_bom.py --root .` | BOM tables are well formed, quantities are positive integers, no prices or personal contact data, relative links resolve |
| PCB | `bash tools/ci/kicad_checks.sh` in `kicad/kicad:10.0.6` (pinned by digest) | ERC, DRC (with schematic parity) and a BOM export for every tracked `*.kicad_pro` |

The electrical contract check reads `decisions.yaml` from openAMRobot/.github at the SHA in the
workflow's `REGISTER_SHA`; it never reads a drive or the documentation site. When the register no
longer states a value the checker expects, the check fails and names the value.

The repository has no KiCad project yet. The PCB step then writes "NOT RUN: no KiCad projects"
to the job summary as a warning, and the container job is skipped.

Known findings that cannot be fixed in a CI change are listed with an open tracking issue in
`tools/ci/hw-check-allow.txt` and `tools/ci/bom-allow.txt`; they are reported as ALLOWED.

### Run locally

```
python3 -m venv .venv && .venv/bin/pip install --no-deps -r tools/ci/requirements.txt
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python tools/ci/check_hw_repo.py --root .
git clone https://github.com/openAMRobot/.github ../.github
.venv/bin/python tools/ci/check_electrical_contract.py --register ../.github/decisions.yaml --require-register
.venv/bin/python tools/ci/check_bom.py --root .
bash tools/ci/kicad_checks.sh
```

## Layers 2 to 4

The nightly integration workflow and the release evidence record are described in the sections
added with them. Hardware-in-the-loop checks for the controller run from openamr-platform-fw on a
self-hosted bench runner; no job in this repository reaches hardware.
