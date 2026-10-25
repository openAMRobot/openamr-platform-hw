#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Check a finishes.yaml and regenerate the table in finish-schedule.md.

The same script lives in openamr-platform-hw and openamr-upperbody-hw (docs/finish/tools/).

  python3 docs/finish/tools/finish_tables.py docs/finish/finishes.yaml \
      [--companion <other repository>/docs/finish/finishes.yaml] \
      [--provenance <openamr-platform-sw>/ros2/src/openamrobot_description/meshes/PROVENANCE.yaml] \
      [--write docs/finish/finish-schedule.md]

Checks: schema keys, finish and status values, palette keys and hex values, unique ids (also
across the companion file), identical palettes in both files, every verify entry names its
check, and (with --provenance) one entry per GLB node id. Exit code 1 on any error.
"""
import argparse
import re
import sys

import yaml

REQUIRED = ["id", "node_id", "part", "name", "location", "material", "current_finish", "colour",
            "ral", "srgb_hex", "finish", "process", "masking", "status", "verify"]
BEGIN, END = "<!-- BEGIN GENERATED: finish table -->", "<!-- END GENERATED: finish table -->"
HEX = re.compile(r"^#[0-9A-F]{6}$")


def load(path):
    with open(path, encoding="utf-8") as stream:
        return yaml.safe_load(stream)


def check(doc, path):
    errors = []
    for key in ["schema", "scope", "repository", "companion", "model", "finish_values",
                "status_values", "palette", "entries"]:
        if key not in doc:
            errors.append(f"{path}: missing top-level key {key}")
    if errors:
        return errors
    if doc["schema"] != "openamrobot-finishes/1":
        errors.append(f"{path}: unknown schema {doc['schema']}")
    for key, colour in doc["palette"].items():
        if not HEX.match(str(colour.get("srgb_hex", ""))):
            errors.append(f"{path}: palette {key} has no valid srgb_hex")
    seen = set()
    for entry in doc["entries"]:
        eid = entry.get("id", "?")
        for key in REQUIRED:
            if key not in entry:
                errors.append(f"{path}: {eid}: missing {key}")
        if eid in seen:
            errors.append(f"{path}: duplicate id {eid}")
        seen.add(eid)
        if entry.get("finish") not in doc["finish_values"]:
            errors.append(f"{path}: {eid}: finish {entry.get('finish')} not in finish_values")
        if entry.get("status") not in doc["status_values"]:
            errors.append(f"{path}: {eid}: status {entry.get('status')} not in status_values")
        if entry.get("status") == "verify" and not entry.get("verify"):
            errors.append(f"{path}: {eid}: status verify needs a verify text")
        if entry.get("status") == "decided" and entry.get("verify"):
            errors.append(f"{path}: {eid}: status decided but a verify text is present")
        colour = entry.get("colour")
        if colour is None:
            if entry.get("srgb_hex") is not None:
                errors.append(f"{path}: {eid}: srgb_hex without a palette colour")
        elif colour not in doc["palette"]:
            errors.append(f"{path}: {eid}: colour {colour} not in the palette")
        elif entry.get("srgb_hex") != doc["palette"][colour]["srgb_hex"]:
            errors.append(f"{path}: {eid}: srgb_hex differs from palette {colour}")
        elif not str(entry.get("ral", "")).startswith(doc["palette"][colour]["ral"]):
            errors.append(f"{path}: {eid}: ral differs from palette {colour}")
        if entry.get("node_id_status", "existing") not in ("existing", "proposed"):
            errors.append(f"{path}: {eid}: node_id_status must be existing or proposed")
    return errors


def cell(value):
    if value is None:
        return "-"
    if isinstance(value, list):
        value = ", ".join(value) if value else "-"
    return str(value).replace("|", "/").replace("\n", " ")


def table(doc):
    rows = ["| Id | Part number or CAD name | GLB node id | Location | Material and current finish "
            "| Proposed colour | Finish and process | Masking and assembly notes | Status |",
            "|---|---|---|---|---|---|---|---|---|"]
    for e in doc["entries"]:
        node = e["node_id"] or "-"
        if e["node_id"] and e.get("node_id_status") == "proposed":
            node = f"{e['node_id']} (proposed)"
        links = e.get("model_link") or e.get("model_links")
        if links:
            node += f"; link {cell(links)}"
        colour = "as delivered" if e["colour"] is None else f"{e['ral']}, {e['srgb_hex']}"
        notes = e["masking"] + (f". {e['notes']}" if e.get("notes") else "")
        status = e["status"] + (f": {e['verify']}" if e.get("verify") else "")
        rows.append("| " + " | ".join(cell(v) for v in [
            e["id"], e["part"], node, e["location"],
            f"{e['material']}; now: {e['current_finish']}", colour,
            f"{e['finish']}; {e['process']}", notes, status]) + " |")
    return "\n".join(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("finishes")
    parser.add_argument("--companion")
    parser.add_argument("--provenance")
    parser.add_argument("--write")
    args = parser.parse_args()

    doc = load(args.finishes)
    errors = check(doc, args.finishes)
    if args.companion:
        other = load(args.companion)
        errors += check(other, args.companion)
        if other.get("palette") != doc.get("palette"):
            errors.append("palettes differ between the two finishes.yaml files")
        if other.get("finish_values") != doc.get("finish_values"):
            errors.append("finish_values differ between the two finishes.yaml files")
        shared = {e["id"] for e in doc["entries"]} & {e["id"] for e in other["entries"]}
        shared |= ({e["node_id"] for e in doc["entries"] if e["node_id"]}
                   & {e["node_id"] for e in other["entries"] if e["node_id"]})
        for item in sorted(shared):
            errors.append(f"id or node id used in both files: {item}")
    if args.provenance:
        nodes = {n["id"] for n in load(args.provenance)["glb"]["nodes"]}
        mapped = [e["node_id"] for e in doc["entries"]
                  if e["node_id"] and e.get("node_id_status", "existing") == "existing"]
        for node in sorted(nodes - set(mapped)):
            errors.append(f"GLB node {node} has no entry")
        for node in sorted(set(mapped) - nodes):
            errors.append(f"entry node {node} is not a GLB node")
        if len(mapped) != len(set(mapped)):
            errors.append("a GLB node id is mapped more than once")
    if args.write and not errors:
        with open(args.write, encoding="utf-8") as stream:
            text = stream.read()
        if BEGIN not in text or END not in text:
            errors.append(f"{args.write}: generated-table markers missing")
        else:
            head, rest = text.split(BEGIN, 1)
            _, tail = rest.split(END, 1)
            with open(args.write, "w", encoding="utf-8") as stream:
                stream.write(f"{head}{BEGIN}\n{table(doc)}\n{END}{tail}")
    for error in errors:
        print(f"ERROR {error}")
    counts = {s: sum(e["status"] == s for e in doc["entries"]) for s in doc.get("status_values", [])}
    print(f"{args.finishes}: {len(doc.get('entries', []))} entries {counts}, {len(errors)} errors")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
