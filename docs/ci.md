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

## Layer 2: nightly integration checks

Workflow `.github/workflows/hardware-nightly.yml` ("Hardware nightly"), daily at 02:17 UTC and on
manual dispatch; never on pull requests. GitHub-hosted runners only.

1. Checks out openamr-platform-hw `main`, openamr-platform-fw `main` and openAMRobot/.github
   `main`, and records the three commit SHAs in the job summary.
2. `tools/ci/nightly_hw.sh` runs every hardware check of layer 1 (self-tests, repository files,
   electrical contract, BOM) and continues after a failure. The electrical contract is checked
   against the register on .github `main` (layer 1 uses the pinned `REGISTER_SHA`), so a register
   change that breaks the contract shows up the next morning.
3. When openamr-platform-fw `main` has `boards/stm32/*/*.ioc`, it runs openamr-platform-fw's
   `tools/ci/check_ioc_contract.py` against this repository's contract; otherwise the check is
   `NOT RUN: no STM32 project on openamr-platform-fw main`.
4. A KiCad container job runs ERC, DRC and the BOM export when a project exists; otherwise `pcb`
   is `NOT RUN: no KiCad projects`.
5. The `evidence` job writes `ci-evidence.json` and uploads it as the artifact `ci-evidence`
   (retention 90 days), with the check logs as `nightly-checks`. The job fails after the upload
   when any check failed.

## Release evidence: ci-evidence.json

`ci-evidence.json` is the input that openamrobot-release reads to prove which exact system was
tested. It is written by `tools/ci/write_evidence.py` and validated against
`tools/ci/ci-evidence.schema.json` (schema_version 1) before upload. openamr-platform-fw writes the
same format from its nightly.

| Field | Meaning |
|---|---|
| `schema_version` | `1` |
| `repository`, `sha`, `ref` | repository and the exact commit checked (`ref` is the branch it was taken from) |
| `workflow`, `run_url`, `date` | workflow name, URL of the run, UTC time the record was written |
| `inputs` | the other checked-out repositories, `repository -> commit SHA` (openamr-platform-fw, openAMRobot/.github) |
| `checks[]` | `name`, `status` (`PASS`, `FAIL` or `NOT RUN`) and `detail` for every check; `experimental: true` marks a check that is recorded but is not a gate (for example the firmware Renode boot) |
| `result` | over the checks not marked experimental: `FAIL` if any failed, `INCOMPLETE` if none failed but one did not run, `PASS` only if all passed |
| `contract` | `repository`, `sha`, `path`, `contract_version` and SHA-256 of `interfaces/electrical/base-controller-io.yaml` |
| `register` | `openAMRobot/.github`, `decisions.yaml` and the register commit SHA |
| `artifacts[]` | files produced by the run with their SHA-256 (firmware images in openamr-platform-fw) |

How openamrobot-release uses it:

- The component SHA in the release manifest must equal `sha`, and the contract SHA and version
  must be the ones the release names.
- `result` must be `PASS` for a release claim; `INCOMPLETE` names the checks that did not run,
  which the release notes list as not verified.
- The record's own SHA-256 is printed in the job summary, and the artifact ID and digest are
  printed by the upload step; the release manifest stores both.
- Records are never edited or regenerated after a release. A later run produces a new record.

The record proves which commits were checked and what the checks reported. It is not hardware,
simulation or safety evidence; hardware-in-the-loop results are recorded separately (openamr-platform-fw,
`docs/hil-bench.md`).

## Layer 3

Hardware-in-the-loop checks for the controller run from openamr-platform-fw on a self-hosted bench
runner; no job in this repository reaches hardware.
