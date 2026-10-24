"""Tests for tools/ci/write_evidence.py and its schema. Run: python3 -m unittest discover -s tests -v"""
import importlib.util
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("write_evidence", ROOT / "tools" / "ci" / "write_evidence.py")
ev = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ev)
SCHEMA = json.loads((ROOT / "tools" / "ci" / "ci-evidence.schema.json").read_text())
CONTRACT = ROOT / "interfaces" / "electrical" / "base-controller-io.yaml"
SHA = "a" * 40


def write(checks, *extra):
    tmp = tempfile.TemporaryDirectory()
    t = Path(tmp.name)
    (t / "checks.tsv").write_text(checks)
    (t / "fw.hex").write_bytes(b":00000001FF\n")
    out = t / "ci-evidence.json"
    with redirect_stdout(io.StringIO()):
        ev.main(["--out", str(out), "--repository", "openAMRobot/openamr-platform-hw", "--sha", SHA,
                 "--ref", "main", "--workflow", "Hardware nightly",
                 "--run-url", "https://github.com/openAMRobot/openamr-platform-hw/actions/runs/1",
                 "--date", "2026-10-24T02:17:00Z", "--input", f"openAMRobot/openamr-platform-fw={'b' * 40}",
                 "--input", f"openAMRobot/.github={'c' * 40}", "--checks", str(t / "checks.tsv"),
                 "--register-sha", "c" * 40, "--contract", str(CONTRACT),
                 "--contract-path", "interfaces/electrical/base-controller-io.yaml",
                 "--artifact", str(t / "fw.hex"), *extra])
    record = json.loads(out.read_text())
    tmp.cleanup()
    return record


class Record(unittest.TestCase):
    def test_all_pass_is_pass_and_validates(self):
        r = write("a\tPASS\tok\nb\tPASS\n")
        jsonschema.validate(r, SCHEMA)
        self.assertEqual(r["result"], "PASS")
        self.assertEqual(r["inputs"]["openAMRobot/.github"], "c" * 40)
        self.assertEqual(r["register"], {"repository": "openAMRobot/.github", "file": "decisions.yaml", "sha": "c" * 40})
        self.assertEqual(r["checks"][0], {"name": "a", "status": "PASS", "detail": "ok"})

    def test_not_run_is_never_pass(self):
        self.assertEqual(write("a\tPASS\nb\tNOT RUN\tno KiCad projects\n")["result"], "INCOMPLETE")

    def test_any_fail_is_fail(self):
        self.assertEqual(write("a\tNOT RUN\nb\tFAIL\nc\tPASS\n")["result"], "FAIL")

    def test_contract_version_and_digest(self):
        r = write("a\tPASS\n")
        self.assertEqual(r["contract"]["contract_version"], "0.1.0")
        self.assertEqual(r["contract"]["sha256"], ev.sha256(CONTRACT))
        self.assertEqual(r["contract"]["path"], "interfaces/electrical/base-controller-io.yaml")

    def test_artifact_digest(self):
        r = write("a\tPASS\n")
        self.assertEqual(len(r["artifacts"]), 1)
        self.assertRegex(r["artifacts"][0]["sha256"], r"^[0-9a-f]{64}$")

    def test_bad_status_is_rejected(self):
        with self.assertRaises(ValueError):
            write("a\tSKIP\n")

    def test_empty_checks_are_rejected(self):
        with self.assertRaises(ValueError):
            write("\n")

    def test_duplicate_checks_are_rejected(self):
        with self.assertRaises(ValueError):
            write("a\tPASS\na\tFAIL\n")

    def test_schema_rejects_a_short_sha(self):
        r = write("a\tPASS\n")
        r["sha"] = "abc123"
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(r, SCHEMA)

    def test_schema_rejects_pass_spelled_skip(self):
        r = write("a\tPASS\n")
        r["checks"][0]["status"] = "SKIP"
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(r, SCHEMA)


if __name__ == "__main__":
    unittest.main()
