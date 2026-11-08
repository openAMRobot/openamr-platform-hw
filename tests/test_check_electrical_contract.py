"""Tests for tools/ci/check_electrical_contract.py. Run: python3 -m unittest discover -s tests -v

Every failing fixture in tests/fixtures/electrical/mutations.yaml becomes one test method.
"""
import copy
import importlib.util
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "ci" / "check_electrical_contract.py"
CONTRACT = ROOT / "interfaces" / "electrical" / "base-controller-io.yaml"
SCHEMA = ROOT / "interfaces" / "electrical" / "base-controller-io.schema.json"
FIXTURES = ROOT / "tests" / "fixtures" / "electrical"
spec = importlib.util.spec_from_file_location("check_electrical_contract", SCRIPT)
chk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(chk)


def set_path(obj, dotted, value):
    keys = dotted.split(".")
    for key in keys[:-1]:
        obj = obj.setdefault(key, {})
    obj[keys[-1]] = value


def mutate(contract, register, case):
    by_name = {s["signal"]: s for s in contract["signals"]}
    if "set" in case:
        for name in case["set"]["signals"]:
            set_path(by_name[name], case["set"]["field"], case["set"]["value"])
    if "top" in case:
        contract[case["top"]["field"]] = case["top"]["value"]
    if "unset" in case:
        for name in case["unset"]["signals"]:
            del by_name[name][case["unset"]["field"]]
    if "delete" in case:
        contract["signals"] = [s for s in contract["signals"] if s["signal"] not in case["delete"]["signals"]]
    if "copy" in case:
        contract["signals"].append(copy.deepcopy(by_name[case["copy"]["signal"]]))
    entry = register["decisions"][0]
    if "register" in case:
        joined = "\n".join(entry["values"])
        assert case["register"]["old"] in joined, case["register"]["old"]
        entry["values"] = joined.replace(case["register"]["old"], case["register"]["new"]).split("\n")
    if "register_id" in case:
        entry["id"] = case["register_id"]["new"]


class Workspace:
    """Write a (possibly mutated) contract and register to a temporary folder."""

    def __init__(self, case=None):
        self.tmp = tempfile.TemporaryDirectory()
        contract = yaml.safe_load(CONTRACT.read_text(encoding="utf-8"))
        register = yaml.safe_load((FIXTURES / "register.yaml").read_text(encoding="utf-8"))
        if case:
            mutate(contract, register, case)
        self.contract = Path(self.tmp.name) / "contract.yaml"
        self.register = Path(self.tmp.name) / "register.yaml"
        self.contract.write_text(yaml.safe_dump(contract, sort_keys=False), encoding="utf-8")
        self.register.write_text(yaml.safe_dump(register, sort_keys=False), encoding="utf-8")

    def run(self, *extra):
        out = io.StringIO()
        report = Path(self.tmp.name) / "report.json"
        with redirect_stdout(out):
            code = chk.main(["--contract", str(self.contract), "--schema", str(SCHEMA),
                             "--register", str(self.register), "--json", str(report), *extra])
        data = json.loads(report.read_text(encoding="utf-8"))
        self.tmp.cleanup()
        return code, out.getvalue(), data


class RealContract(unittest.TestCase):
    def test_checked_in_contract_passes_every_rule(self):
        code, out, data = Workspace().run("--register-sha", "fixture")
        self.assertEqual(code, 0, out)
        self.assertEqual(set(data["results"].values()), {"PASS"}, out)
        self.assertEqual(set(data["results"]), set(chk.RULES))

    def test_report_names_version_and_digest(self):
        _, out, data = Workspace().run()
        self.assertEqual(data["contract_version"], "0.1.0")
        self.assertRegex(data["contract_sha256"], r"^[0-9a-f]{64}$")

    def test_reference_counts(self):
        signals = yaml.safe_load(CONTRACT.read_text(encoding="utf-8"))["signals"]
        self.assertEqual(len(chk.device_uarts(signals, "MB7060")), 4)
        self.assertEqual(len(chk.device_uarts(signals, "TF-Luna")), 2)
        not_required = sorted(s["gpio"] for s in signals if s["status"] == "not_required")
        self.assertEqual(not_required, ["PA0", "PC12", "PE1", "PF7"])

    def test_without_register_is_not_run_not_pass(self):
        out = io.StringIO()
        with redirect_stdout(out):
            code = chk.main(["--contract", str(CONTRACT), "--schema", str(SCHEMA)])
        self.assertEqual(code, 0)
        self.assertIn("NOT RUN register", out.getvalue())
        with redirect_stdout(io.StringIO()):
            code = chk.main(["--contract", str(CONTRACT), "--schema", str(SCHEMA), "--require-register"])
        self.assertEqual(code, 1)

    def test_schema_failure_marks_other_rules_not_run(self):
        case = {"set": {"signals": ["imu_cs"], "field": "gpio", "value": "PZ1"}}
        code, _, data = Workspace(case).run()
        self.assertEqual(code, 1)
        self.assertEqual(data["results"]["schema"], "FAIL")
        self.assertEqual({data["results"][r] for r in chk.RULES[1:]}, {"NOT RUN"})


class Fixtures(unittest.TestCase):
    """One generated test per failing fixture."""


def make_test(case):
    def test(self):
        code, out, data = Workspace(case).run()
        self.assertEqual(code, 1, out)
        self.assertEqual(data["results"][case["rule"]], "FAIL", out)
        messages = " | ".join(data["details"][case["rule"]])
        self.assertIn(case["expect"], messages)
    return test


CASES = yaml.safe_load((FIXTURES / "mutations.yaml").read_text(encoding="utf-8"))
for index, case in enumerate(CASES):
    slug = "".join(c if c.isalnum() else "_" for c in case["name"].lower())
    setattr(Fixtures, f"test_{index:02d}_{case['rule'].replace('-', '_')}_{slug}", make_test(case))


class EveryRuleHasAFixture(unittest.TestCase):
    def test_every_rule_fails_in_at_least_one_fixture(self):
        self.assertEqual({c["rule"] for c in CASES}, set(chk.RULES))


if __name__ == "__main__":
    unittest.main()
