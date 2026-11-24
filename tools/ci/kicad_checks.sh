#!/usr/bin/env bash
# ERC, DRC and BOM export for every tracked *.kicad_pro in the repository.
#
# Usage: tools/ci/kicad_checks.sh [--list] [OUT_DIR]
#   --list   print the projects found (one per line) and exit 0; used by the workflow to decide
#            whether the KiCad container job runs at all
#   OUT_DIR  where reports go (default: build/kicad)
#
# With no KiCad project the script writes "NOT RUN: no KiCad projects" as a warning to the job
# summary and exits 0: NOT RUN is reported, never PASS. Otherwise every project needs its
# .kicad_sch and .kicad_pcb next to the .kicad_pro; any ERC or DRC violation, a missing file or a
# failed export exits 1. KICAD_CLI overrides the kicad-cli binary (tests use a stub).
set -euo pipefail

KICAD_CLI="${KICAD_CLI:-kicad-cli}"
SUMMARY="${GITHUB_STEP_SUMMARY:-/dev/null}"
list_only=0
if [[ "${1:-}" == "--list" ]]; then list_only=1; shift; fi
out="${1:-build/kicad}"

mapfile -t projects < <(git ls-files -- '*.kicad_pro' | LC_ALL=C sort)

if (( list_only )); then
  printf '%s\n' "${projects[@]}"
  exit 0
fi

if (( ${#projects[@]} == 0 )); then
  echo "::warning title=PCB checks::NOT RUN: no KiCad projects"
  echo "NOT RUN: no KiCad projects (no tracked *.kicad_pro)" >> "$SUMMARY"
  exit 0
fi

mkdir -p "$out"
"$KICAD_CLI" version | tee "$out/kicad-cli-version.txt"
echo "### PCB checks (kicad-cli $(cat "$out/kicad-cli-version.txt"))" >> "$SUMMARY"
failed=0
for pro in "${projects[@]}"; do
  base="${pro%.kicad_pro}"
  name="$(echo "$base" | tr '/' '_')"
  sch="$base.kicad_sch"
  pcb="$base.kicad_pcb"
  for f in "$sch" "$pcb"; do
    if [[ ! -f "$f" ]]; then
      echo "::error file=$pro::$f is missing; a KiCad project needs its schematic and board"
      echo "- FAIL $pro: $f missing" >> "$SUMMARY"
      failed=1
      continue 2
    fi
  done
  if "$KICAD_CLI" sch erc --severity-all --exit-code-violations --format json \
       --output "$out/$name.erc.json" "$sch"; then
    echo "- PASS ERC $sch" >> "$SUMMARY"
  else
    echo "::error file=$sch::ERC violations (report $out/$name.erc.json)"
    echo "- FAIL ERC $sch" >> "$SUMMARY"
    failed=1
  fi
  if "$KICAD_CLI" pcb drc --severity-all --schematic-parity --exit-code-violations --format json \
       --output "$out/$name.drc.json" "$pcb"; then
    echo "- PASS DRC $pcb" >> "$SUMMARY"
  else
    echo "::error file=$pcb::DRC violations (report $out/$name.drc.json)"
    echo "- FAIL DRC $pcb" >> "$SUMMARY"
    failed=1
  fi
  if "$KICAD_CLI" sch export bom --output "$out/$name.bom.csv" "$sch"; then
    echo "- PASS BOM export $out/$name.bom.csv" >> "$SUMMARY"
  else
    echo "::error file=$sch::BOM export failed"
    echo "- FAIL BOM export $sch" >> "$SUMMARY"
    failed=1
  fi
done
exit "$failed"
