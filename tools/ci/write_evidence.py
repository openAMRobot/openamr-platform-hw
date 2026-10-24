#!/usr/bin/env python3
"""Write ci-evidence.json, the CI evidence record handed to openamrobot-release.

The record says which exact commits a nightly run checked and what each check reported. Format:
tools/ci/ci-evidence.schema.json (schema_version 1), described in docs/ci.md. A check reported
NOT RUN is never counted as PASS: the record's result is PASS only when every check passed,
FAIL when any failed, otherwise INCOMPLETE. The record is validated against the schema before it
is written. openamr-platform-fw keeps a copy of this file and the schema; keep them identical.

Usage:
  write_evidence.py --out ci-evidence.json --repository openAMRobot/openamr-platform-hw \
    --sha <sha> --ref main --workflow "Hardware nightly" --run-url <url> \
    --input openAMRobot/openamr-platform-fw=<sha> --input openAMRobot/.github=<sha> \
    --checks checks.tsv --register-sha <sha> \
    [--contract interfaces/electrical/base-controller-io.yaml --contract-repository R --contract-sha S] \
    [--artifact path ...]
checks.tsv: one check per line, "<name><TAB><PASS|FAIL|NOT RUN>[<TAB>detail[<TAB>experimental]]".
A check marked experimental is recorded but is not a gate: it does not count towards result.
"""
import argparse
import datetime
import hashlib
import json
import sys
from pathlib import Path

import jsonschema
import yaml

SCHEMA = Path(__file__).resolve().parent / "ci-evidence.schema.json"
STATUSES = ("PASS", "FAIL", "NOT RUN")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def read_checks(path):
    checks = []
    for number, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) < 2 or parts[1] not in STATUSES:
            raise ValueError(f"{path}:{number}: expected '<name>\\t<{'|'.join(STATUSES)}>[\\tdetail]', got {line!r}")
        check = {"name": parts[0], "status": parts[1]}
        if len(parts) > 2 and parts[2]:
            check["detail"] = parts[2]
        if len(parts) > 3:
            if parts[3] != "experimental":
                raise ValueError(f"{path}:{number}: fourth field must be 'experimental', got {parts[3]!r}")
            check["experimental"] = True
        checks.append(check)
    if not checks:
        raise ValueError(f"{path}: no checks; an evidence record without checks proves nothing")
    names = [c["name"] for c in checks]
    if len(names) != len(set(names)):
        raise ValueError(f"{path}: duplicate check names")
    return checks


def overall(checks):
    gating = [c for c in checks if not c.get("experimental")]
    if not gating:
        raise ValueError("every check is experimental; an evidence record needs at least one gating check")
    statuses = {c["status"] for c in gating}
    if "FAIL" in statuses:
        return "FAIL"
    return "INCOMPLETE" if "NOT RUN" in statuses else "PASS"


def build(a):
    checks = read_checks(a.checks)
    contract = None
    if a.contract and Path(a.contract).is_file():
        data = yaml.safe_load(Path(a.contract).read_text(encoding="utf-8"))
        contract = {"repository": a.contract_repository or a.repository, "sha": a.contract_sha or a.sha,
                    "path": a.contract_path or a.contract, "contract_version": str(data["contract_version"]),
                    "sha256": sha256(a.contract)}
    inputs = {}
    for item in a.input:
        repo, _, sha = item.partition("=")
        inputs[repo] = sha
    return {
        "schema_version": 1,
        "repository": a.repository,
        "sha": a.sha,
        "ref": a.ref,
        "workflow": a.workflow,
        "run_url": a.run_url,
        "date": a.date or datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "inputs": inputs,
        "checks": checks,
        "result": overall(checks),
        "contract": contract,
        "register": {"repository": "openAMRobot/.github", "file": "decisions.yaml", "sha": a.register_sha},
        "artifacts": [{"path": p, "sha256": sha256(p)} for p in a.artifact],
    }


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--out", required=True)
    p.add_argument("--repository", required=True)
    p.add_argument("--sha", required=True)
    p.add_argument("--ref", required=True)
    p.add_argument("--workflow", required=True)
    p.add_argument("--run-url", required=True)
    p.add_argument("--date", help="UTC timestamp (default: now)")
    p.add_argument("--input", action="append", default=[], help="REPOSITORY=SHA of another checked-out repository")
    p.add_argument("--checks", required=True)
    p.add_argument("--register-sha", required=True)
    p.add_argument("--contract")
    p.add_argument("--contract-path", help="path of the contract inside its repository (default: --contract)")
    p.add_argument("--contract-repository")
    p.add_argument("--contract-sha")
    p.add_argument("--artifact", action="append", default=[])
    a = p.parse_args(argv)
    record = build(a)
    jsonschema.Draft202012Validator(json.loads(SCHEMA.read_text(encoding="utf-8"))).validate(record)
    Path(a.out).write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(f"{a.out}: result {record['result']}, {len(record['checks'])} checks, sha256 {sha256(a.out)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
