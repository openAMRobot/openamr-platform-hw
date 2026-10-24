"""Tests for tools/ci/nightly_hw.sh: the ioc-contract and PCB branches. Run: python3 -m unittest discover -s tests -v

OPENAMR_NIGHTLY_INNER=1 makes the script record its own self-test step as NOT RUN, so these
tests do not start the suite recursively.
"""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "ci" / "nightly_hw.sh"
REGISTER = ROOT / "tests" / "fixtures" / "electrical" / "register.yaml"


class Nightly(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        t = Path(self.tmp.name)
        self.gh = t / "dotgithub"
        self.gh.mkdir()
        shutil.copy(REGISTER, self.gh / "decisions.yaml")
        subprocess.run(["git", "init", "-q", str(self.gh)], check=True)
        subprocess.run(["git", "-C", str(self.gh), "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q",
                        "--allow-empty", "-m", "fixture"], check=True)
        self.fw = t / "fw"
        self.fw.mkdir()
        self.out = t / "out"
        bindir = Path(sys.executable).parent
        self.env = dict(os.environ, OPENAMR_NIGHTLY_INNER="1", PATH=f"{bindir}{os.pathsep}{os.environ['PATH']}")

    def tearDown(self):
        self.tmp.cleanup()

    def run_script(self):
        r = subprocess.run(["bash", str(SCRIPT), str(ROOT), str(self.fw), str(self.gh), str(self.out)],
                           env=self.env, capture_output=True, text=True)
        rows = [line.split("\t") for line in (self.out / "checks.tsv").read_text().splitlines()]
        return r, {row[0]: row[1:] for row in rows}

    def test_no_stm32_project_is_not_run(self):
        r, rows = self.run_script()
        self.assertEqual(rows["ioc-contract"], ["NOT RUN", "no STM32 project on openamr-platform-fw main"])
        self.assertEqual(rows["pcb"], ["NOT RUN", "no KiCad projects"])
        self.assertEqual(rows["hw-self-tests"][0], "NOT RUN")
        self.assertEqual(rows["electrical-contract"][0], "PASS", r.stdout + r.stderr)
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_ioc_without_checker_is_not_run(self):
        (self.fw / "boards/stm32/P").mkdir(parents=True)
        (self.fw / "boards/stm32/P/P.ioc").write_text("PB8.Signal=UART4_RX\n")
        _, rows = self.run_script()
        self.assertEqual(rows["ioc-contract"], ["NOT RUN", "check_ioc_contract.py is not on openamr-platform-fw main"])

    def test_failing_ioc_check_fails_the_run(self):
        (self.fw / "boards/stm32/P").mkdir(parents=True)
        (self.fw / "boards/stm32/P/P.ioc").write_text("PB8.Signal=UART4_RX\n")
        (self.fw / "tools/ci").mkdir(parents=True)
        (self.fw / "tools/ci/check_ioc_contract.py").write_text("import sys\nprint('stub: 1 error')\nsys.exit(1)\n")
        r, rows = self.run_script()
        self.assertEqual(rows["ioc-contract"][0], "FAIL")
        self.assertEqual(r.returncode, 1)
        self.assertIn("stub: 1 error", (self.out / "logs/ioc-contract.log").read_text())


if __name__ == "__main__":
    unittest.main()
