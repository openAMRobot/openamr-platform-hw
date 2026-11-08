"""Tests for tools/ci/kicad_checks.sh with a stub kicad-cli. Run: python3 -m unittest discover -s tests -v

The stub records each call and fails ERC or DRC when the project folder holds a file named
ERC_FAIL or DRC_FAIL. These tests cover the job logic only; they do not run KiCad.
"""
import os
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "ci" / "kicad_checks.sh"
STUB = textwrap.dedent("""\
    #!/usr/bin/env bash
    echo "$*" >> "$STUB_LOG"
    [[ "$1" == version ]] && { echo 10.0.6-stub; exit 0; }
    target="${@: -1}"
    dir="$(dirname "$target")"
    [[ "$1 $2" == "sch erc" && -f "$dir/ERC_FAIL" ]] && exit 5
    [[ "$1 $2" == "pcb drc" && -f "$dir/DRC_FAIL" ]] && exit 5
    exit 0
    """)


class KicadChecks(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "repo"
        self.root.mkdir()
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        stub = Path(self.tmp.name) / "kicad-cli"
        stub.write_text(STUB)
        stub.chmod(0o755)
        self.log = Path(self.tmp.name) / "calls.log"
        self.summary = Path(self.tmp.name) / "summary.md"
        self.env = dict(os.environ, KICAD_CLI=str(stub), STUB_LOG=str(self.log),
                        GITHUB_STEP_SUMMARY=str(self.summary))

    def tearDown(self):
        self.tmp.cleanup()

    def add(self, *files):
        for f in files:
            p = self.root / f
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text("(kicad fixture)\n")
        subprocess.run(["git", "-C", str(self.root), "add", "-A"], check=True)

    def run_script(self, *args):
        return subprocess.run(["bash", str(SCRIPT), *args], cwd=self.root, env=self.env,
                              capture_output=True, text=True)

    def test_bash_syntax(self):
        self.assertEqual(subprocess.run(["bash", "-n", str(SCRIPT)]).returncode, 0)

    def test_no_project_is_not_run_not_pass(self):
        self.add("README.md")
        r = self.run_script()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("::warning title=PCB checks::NOT RUN: no KiCad projects", r.stdout)
        self.assertIn("NOT RUN: no KiCad projects", self.summary.read_text())
        self.assertNotIn("PASS", self.summary.read_text())
        self.assertFalse(self.log.exists(), "kicad-cli must not be called without a project")

    def test_list_mode(self):
        self.add("electrical/pcb/b/b.kicad_pro", "electrical/pcb/a/a.kicad_pro")
        r = self.run_script("--list")
        self.assertEqual(r.stdout.split(), ["electrical/pcb/a/a.kicad_pro", "electrical/pcb/b/b.kicad_pro"])

    def test_clean_project_runs_erc_drc_and_bom(self):
        self.add("electrical/pcb/io/io.kicad_pro", "electrical/pcb/io/io.kicad_sch", "electrical/pcb/io/io.kicad_pcb")
        r = self.run_script(str(Path(self.tmp.name) / "out"))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        calls = self.log.read_text()
        self.assertIn("sch erc --severity-all --exit-code-violations", calls)
        self.assertIn("pcb drc --severity-all --schematic-parity --exit-code-violations", calls)
        self.assertIn("sch export bom", calls)
        summary = self.summary.read_text()
        for line in ("PASS ERC", "PASS DRC", "PASS BOM export"):
            self.assertIn(line, summary)

    def test_erc_violation_fails(self):
        self.add("p/x.kicad_pro", "p/x.kicad_sch", "p/x.kicad_pcb", "p/ERC_FAIL")
        r = self.run_script()
        self.assertEqual(r.returncode, 1)
        self.assertIn("::error file=p/x.kicad_sch::ERC violations", r.stdout)

    def test_drc_violation_fails(self):
        self.add("p/x.kicad_pro", "p/x.kicad_sch", "p/x.kicad_pcb", "p/DRC_FAIL")
        r = self.run_script()
        self.assertEqual(r.returncode, 1)
        self.assertIn("::error file=p/x.kicad_pcb::DRC violations", r.stdout)

    def test_project_without_board_fails(self):
        self.add("p/x.kicad_pro", "p/x.kicad_sch")
        r = self.run_script()
        self.assertEqual(r.returncode, 1)
        self.assertIn("p/x.kicad_pcb is missing", r.stdout)


if __name__ == "__main__":
    unittest.main()
