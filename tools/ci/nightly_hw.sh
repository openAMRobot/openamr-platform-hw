#!/usr/bin/env bash
# Layer 2 hardware checks across pinned commits, for the "Hardware nightly" workflow.
# Usage: tools/ci/nightly_hw.sh HW_DIR FW_DIR DOTGITHUB_DIR OUT_DIR
#   HW_DIR         checkout of openamr-platform-hw (the commit under test)
#   FW_DIR         checkout of openamr-platform-fw main
#   DOTGITHUB_DIR  checkout of openAMRobot/.github main (decisions register)
# Writes OUT_DIR/checks.tsv ("<name>\t<PASS|FAIL|NOT RUN>\t<detail>"), OUT_DIR/logs/<name>.log and
# OUT_DIR/electrical-contract.json. Every check runs even after a failure; NOT RUN is never PASS.
# The PCB line is written here only when there is no KiCad project (the workflow's container job
# reports it otherwise). Exit 1 if any check failed. Python packages: tools/ci/requirements.txt.
set -uo pipefail
hw="$(cd "$1" && pwd)"; fw="$(cd "$2" && pwd)"; gh="$(cd "$3" && pwd)"; out="$4"
mkdir -p "$out/logs"; out="$(cd "$out" && pwd)"
: > "$out/checks.tsv"
failed=0

record() { printf '%s\t%s\t%s\n' "$1" "$2" "$3" >> "$out/checks.tsv"; echo "$2 $1${3:+: $3}"; }

run() {  # run NAME DETAIL CMD...: PASS on exit 0, FAIL otherwise
  local name="$1" detail="$2"; shift 2
  if (cd "$hw" && "$@") > "$out/logs/$name.log" 2>&1; then
    record "$name" PASS "$detail"
  else
    record "$name" FAIL "$detail (log logs/$name.log)"; failed=1
  fi
}

suite() {  # unittest with the zero-test guard
  python -m unittest discover -s tests -v 2>&1 && return 0
  return 1
}
if [ "${OPENAMR_NIGHTLY_INNER:-}" = 1 ]; then
  # set by tests/test_nightly_hw.py, which runs this script from inside the suite
  record hw-self-tests "NOT RUN" "called from inside the test suite"
elif (cd "$hw" && suite) > "$out/logs/hw-self-tests.log" 2>&1 && grep -qE '^Ran [1-9][0-9]* tests?' "$out/logs/hw-self-tests.log"; then
  record hw-self-tests PASS "$(grep -E '^Ran ' "$out/logs/hw-self-tests.log" | tail -1)"
else
  record hw-self-tests FAIL "$(grep -E '^Ran ' "$out/logs/hw-self-tests.log" | tail -1) (log logs/hw-self-tests.log)"; failed=1
fi

run hw-repo-files "links, formats, sizes, attributes, datasheet index" python tools/ci/check_hw_repo.py --root .
run electrical-contract "register openAMRobot/.github $(git -C "$gh" rev-parse HEAD)" \
    python tools/ci/check_electrical_contract.py --register "$gh/decisions.yaml" \
    --register-sha "$(git -C "$gh" rev-parse HEAD)" --require-register --json "$out/electrical-contract.json"
run bom "manufacturing/bom" python tools/ci/check_bom.py --root .

projects=$(cd "$hw" && bash tools/ci/kicad_checks.sh --list | grep -c . || true)
if [ "$projects" = 0 ]; then
  record pcb "NOT RUN" "no KiCad projects"
fi

shopt -s nullglob
iocs=("$fw"/boards/stm32/*/*.ioc)
if (( ${#iocs[@]} == 0 )); then
  record ioc-contract "NOT RUN" "no STM32 project on openamr-platform-fw main"
elif [ ! -f "$fw/tools/ci/check_ioc_contract.py" ]; then
  record ioc-contract "NOT RUN" "check_ioc_contract.py is not on openamr-platform-fw main"
else
  status=0
  for ioc in "${iocs[@]}"; do
    python "$fw/tools/ci/check_ioc_contract.py" "$ioc" --contract "$hw/interfaces/electrical/base-controller-io.yaml" \
      --contract-sha "$(git -C "$hw" rev-parse HEAD)" >> "$out/logs/ioc-contract.log" 2>&1 || status=1
  done
  if (( status == 0 )); then
    record ioc-contract PASS "${#iocs[@]} .ioc against this contract"
  else
    record ioc-contract FAIL "${#iocs[@]} .ioc against this contract (log logs/ioc-contract.log)"; failed=1
  fi
fi
exit "$failed"
