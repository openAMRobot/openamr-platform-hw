#!/usr/bin/env python3
"""Check the base-controller I/O contract (interfaces/electrical/base-controller-io.yaml).

Rules, each reported PASS, FAIL or NOT RUN:
  schema           the file validates against base-controller-io.schema.json
  unique-signal    every signal name appears once
  unique-gpio      no GPIO carries two signals (not_required entries are not signals; they may
                   only share a pin with a reserved entry)
  reserved-pin     no signal sits on a pin reserved by the board
  not-required-af  every not_required pin has no alternate function
  af-present       verified and proposed alternate-function pins (not GPIO, BOARD, DEBUG, RCC)
                   carry an AF number
  peripheral       entries of one peripheral agree on its settings
  counts           four MB7060 and two TF-Luna, each on its own UART, one trigger per MB7060
  register         values agree with the register entry BASE-CONTROLLER-IO in decisions.yaml:
                   controller and board, MB7060 baud, frame and receive inversion, CAN1 traction,
                   CAN2 BMS, CAN3 upper-body auxiliary, micro-ROS over UDP on Ethernet to the
                   Jetson, IMU on a dedicated SPI in the register's mode

The register is read from a checkout of openAMRobot/.github at a pinned SHA (--register). If the
register text no longer contains a value this checker expects, that is a FAIL naming the value,
never a silent PASS. A PASS proves the file is consistent with itself and the register text, not
that the electronics behave as designed. Exit code 1 on any FAIL.
"""
import argparse
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import jsonschema
import yaml

RULES = ["schema", "unique-signal", "unique-gpio", "reserved-pin", "not-required-af",
         "af-present", "peripheral", "counts", "register"]
NO_AF_PERIPHERALS = {"GPIO", "BOARD", "DEBUG", "RCC"}
BUS_KEYS = ("baud", "frame", "rx_invert", "mode", "spi_mode", "max_clock_hz", "bus", "role",
            "bitrate", "interface", "transport", "peer")
NUMBERS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8}
CAN_ROLES = {"traction": "traction", "BMS": "bms", "upper-body auxiliary": "upper_body_auxiliary"}


def used(entry):
    """A pin that carries a signal: allocated, and neither reserved nor not_required."""
    return entry["gpio"] is not None and entry["status"] not in ("reserved", "not_required")


def check_schema(contract, schema):
    validator = jsonschema.Draft202012Validator(schema)
    return [f"{'/'.join(str(p) for p in e.absolute_path) or '<root>'}: {e.message}"
            for e in sorted(validator.iter_errors(contract), key=lambda e: list(e.absolute_path))]


def check_unique_signal(signals):
    return [f"signal {name} appears {n} times" for name, n in Counter(s["signal"] for s in signals).items() if n > 1]


def check_unique_gpio(signals):
    errors = []
    by_pin = defaultdict(list)
    for s in signals:
        if s["gpio"]:
            by_pin[s["gpio"]].append(s)
    for pin, entries in sorted(by_pin.items()):
        carrying = [e["signal"] for e in entries if used(e)]
        reserved = [e["signal"] for e in entries if e["status"] == "reserved"]
        spare = [e["signal"] for e in entries if e["status"] == "not_required"]
        if len(carrying) > 1:
            errors.append(f"{pin} used twice: {', '.join(carrying)}")
        if len(reserved) > 1:
            errors.append(f"{pin} reserved twice: {', '.join(reserved)}")
        if spare and carrying:
            errors.append(f"{pin} is marked not_required ({', '.join(spare)}) and also carries {', '.join(carrying)}")
    return errors


def check_reserved(signals):
    reserved = {s["gpio"]: s["signal"] for s in signals if s["status"] == "reserved"}
    return [f"{s['signal']} on {s['gpio']}, which is reserved for {reserved[s['gpio']]}"
            for s in signals if used(s) and s["gpio"] in reserved]


def check_not_required_af(signals):
    return [f"{s['signal']} on {s['gpio']} is not_required but has AF{s['af']}"
            for s in signals if s["status"] == "not_required" and s["af"] is not None]


def check_af_present(signals):
    return [f"{s['signal']} on {s['gpio']} ({s['function']}, {s['status']}) has no AF number"
            for s in signals
            if s["status"] in ("verified", "proposed") and s["peripheral"] not in NO_AF_PERIPHERALS
            and s["af"] is None]


def check_peripheral(signals):
    errors = []
    groups = defaultdict(list)
    for s in signals:
        if used(s) and s["peripheral"] not in NO_AF_PERIPHERALS:
            groups[s["peripheral"]].append(s)
    for peripheral, entries in sorted(groups.items()):
        for key in BUS_KEYS:
            values = {json.dumps(e["settings"].get(key)) for e in entries}
            if len(values) > 1:
                errors.append(f"{peripheral} entries disagree on {key}: {', '.join(sorted(values))}")
    return errors


def device_uarts(signals, device):
    return {s["peripheral"] for s in signals if s["device"] == device and used(s) and "ART" in s["peripheral"]}


def check_counts(signals):
    errors = []
    for device, want in (("MB7060", 4), ("TF-Luna", 2)):
        uarts = device_uarts(signals, device)
        if len(uarts) != want:
            errors.append(f"{device}: {len(uarts)} UARTs ({', '.join(sorted(uarts)) or 'none'}), expected {want}")
        for u in sorted(uarts):
            others = {s["device"] for s in signals if s["peripheral"] == u and used(s)} - {device}
            if others:
                errors.append(f"{u} is shared by {device} and {', '.join(sorted(others))}; one UART per sensor")
    rx = [s for s in signals if s["device"] == "MB7060" and used(s) and s["function"].endswith("_RX")]
    triggers = [s for s in signals if s["device"] == "MB7060" and s["peripheral"] == "GPIO"
                and s["direction"] == "output" and s["status"] != "not_required"]
    if len(triggers) != len(rx):
        errors.append(f"MB7060: {len(triggers)} trigger GPIOs for {len(rx)} sensors; one trigger each")
    return errors


def register_entry(register, decision_id):
    for entry in register.get("decisions", []):
        if entry.get("id") == decision_id:
            return entry
    return None


def check_register(contract, register):
    """Compare the contract with the text of BASE-CONTROLLER-IO. Each expectation is parsed from
    the register; a value the checker cannot find in the register is itself a FAIL."""
    errors = []
    signals = contract["signals"]
    entry = register_entry(register, "BASE-CONTROLLER-IO")
    if entry is None:
        return ["register has no entry BASE-CONTROLLER-IO"]
    if entry.get("status") != "recorded":
        errors.append(f"BASE-CONTROLLER-IO status is {entry.get('status')}, expected recorded")
    text = " | ".join(str(v) for v in entry.get("values", []))

    def find(pattern, what):
        m = re.search(pattern, text)
        if not m:
            errors.append(f"register BASE-CONTROLLER-IO no longer states {what}; update this checker "
                          "and the contract through a contract change request")
        return m

    m = find(r"Base controller (\S+) on (\S+)", "the controller and board")
    if m:
        if contract["controller"] != m.group(1):
            errors.append(f"controller {contract['controller']}, register says {m.group(1)}")
        if contract["board"] != m.group(2):
            errors.append(f"board {contract['board']}, register says {m.group(2)}")

    m = find(r"(\w+) MaxBotix MB7060.*?(\d+) (\d[NEO]\d)( with receive inversion)?", "the MB7060 UART settings")
    if m:
        count, baud, frame, invert = NUMBERS.get(m.group(1), -1), int(m.group(2)), m.group(3), bool(m.group(4))
        if len(device_uarts(signals, "MB7060")) != count:
            errors.append(f"register says {m.group(1)} MB7060, contract has {len(device_uarts(signals, 'MB7060'))}")
        for s in signals:
            if s["device"] == "MB7060" and used(s) and s["function"].endswith("_RX"):
                got = s["settings"]
                if got.get("baud") != baud:
                    errors.append(f"{s['signal']}: baud {got.get('baud')}, register says {baud}")
                if got.get("frame") != frame:
                    errors.append(f"{s['signal']}: frame {got.get('frame')}, register says {frame}")
                if got.get("rx_invert") is not invert:
                    errors.append(f"{s['signal']}: rx_invert {got.get('rx_invert')}, register says "
                                  f"{'receive inversion' if invert else 'no inversion'}")

    m = find(r"(\w+) Benewake TF-Luna", "the TF-Luna count")
    if m and len(device_uarts(signals, "TF-Luna")) != NUMBERS.get(m.group(1), -1):
        errors.append(f"register says {m.group(1)} TF-Luna, contract has {len(device_uarts(signals, 'TF-Luna'))}")

    m = find(r"IMU on a dedicated SPI, Mode (\d)", "the IMU SPI mode")
    if m:
        spi = {s["peripheral"] for s in signals if used(s) and s["peripheral"].startswith("SPI")
               and s["device"].startswith("ICM-42688")}
        if len(spi) != 1:
            errors.append(f"IMU uses {len(spi)} SPI peripherals ({', '.join(sorted(spi)) or 'none'}), expected one")
        for p in spi:
            entries = [s for s in signals if s["peripheral"] == p and used(s)]
            others = {s["device"] for s in entries} - {e["device"] for e in entries if e["device"].startswith("ICM-42688")}
            if others:
                errors.append(f"{p} is not dedicated to the IMU: also {', '.join(sorted(others))}")
            for s in entries:
                if s["settings"].get("spi_mode") != int(m.group(1)):
                    errors.append(f"{s['signal']}: spi_mode {s['settings'].get('spi_mode')}, register says Mode {m.group(1)}")

    for bus, label in (("CAN1", "traction"), ("CAN2", "BMS"), ("CAN3", "upper-body auxiliary")):
        if find(rf"{bus} [^,|;]*{label}", f"{bus} {label}"):
            for s in signals:
                if used(s) and s["settings"].get("bus") == bus and s["settings"].get("role") != CAN_ROLES[label]:
                    errors.append(f"{s['signal']}: {bus} role {s['settings'].get('role')}, register says {label}")
            if not any(used(s) and s["settings"].get("bus") == bus for s in signals):
                errors.append(f"no contract signal on {bus} ({label})")

    m = find(r"MCU to (\w+) over Ethernet, (micro-ROS over UDP)", "micro-ROS over UDP on Ethernet")
    if m:
        eth = [s for s in signals if s["peripheral"] == "ETH" and used(s)]
        if not eth:
            errors.append("no Ethernet signals in the contract")
        for s in eth:
            if s["settings"].get("transport") != m.group(2):
                errors.append(f"{s['signal']}: transport {s['settings'].get('transport')}, register says {m.group(2)}")
            if s["settings"].get("peer") != m.group(1):
                errors.append(f"{s['signal']}: peer {s['settings'].get('peer')}, register says {m.group(1)}")
    return errors


def run(contract_path, schema_path, register_path):
    """Return (results, details): results maps rule -> PASS | FAIL | NOT RUN."""
    contract = yaml.safe_load(Path(contract_path).read_text(encoding="utf-8"))
    schema = json.loads(Path(schema_path).read_text(encoding="utf-8"))
    results, details = {}, {}
    errors = check_schema(contract, schema)
    results["schema"], details["schema"] = ("FAIL" if errors else "PASS"), errors
    if errors:
        for rule in RULES[1:]:
            results[rule], details[rule] = "NOT RUN", ["schema invalid"]
        return contract, results, details
    signals = contract["signals"]
    checks = {
        "unique-signal": lambda: check_unique_signal(signals),
        "unique-gpio": lambda: check_unique_gpio(signals),
        "reserved-pin": lambda: check_reserved(signals),
        "not-required-af": lambda: check_not_required_af(signals),
        "af-present": lambda: check_af_present(signals),
        "peripheral": lambda: check_peripheral(signals),
        "counts": lambda: check_counts(signals),
    }
    for rule, fn in checks.items():
        errors = fn()
        results[rule], details[rule] = ("FAIL" if errors else "PASS"), errors
    if register_path:
        register = yaml.safe_load(Path(register_path).read_text(encoding="utf-8"))
        errors = check_register(contract, register)
        results["register"], details["register"] = ("FAIL" if errors else "PASS"), errors
    else:
        results["register"], details["register"] = "NOT RUN", ["no --register given"]
    return contract, results, details


def main(argv=None):
    here = Path(__file__).resolve().parents[2] / "interfaces" / "electrical"
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--contract", default=str(here / "base-controller-io.yaml"))
    p.add_argument("--schema", default=str(here / "base-controller-io.schema.json"))
    p.add_argument("--register", help="decisions.yaml from a checkout of openAMRobot/.github")
    p.add_argument("--register-sha", default="", help="SHA of that checkout, for the report")
    p.add_argument("--require-register", action="store_true", help="NOT RUN of the register rule fails")
    p.add_argument("--json", help="write results as JSON here")
    a = p.parse_args(argv)
    contract, results, details = run(a.contract, a.schema, a.register)
    for rule in RULES:
        status = results[rule]
        if status == "FAIL":
            for message in details[rule]:
                print(f"::error file={a.contract}::[{rule}] {message}")
        elif status == "NOT RUN":
            print(f"::warning file={a.contract}::[{rule}] NOT RUN: {'; '.join(details[rule])}")
        print(f"{status:7} {rule}")
    digest = hashlib.sha256(Path(a.contract).read_bytes()).hexdigest()
    version = contract.get("contract_version") if isinstance(contract, dict) else None
    print(f"contract_version {version}, sha256 {digest}" + (f", register {a.register_sha}" if a.register_sha else ""))
    if a.json:
        Path(a.json).write_text(json.dumps({"contract_version": version, "contract_sha256": digest,
                                            "register_sha": a.register_sha or None,
                                            "results": results, "details": details}, indent=2) + "\n",
                                encoding="utf-8")
    failed = "FAIL" in results.values() or (a.require_register and results["register"] != "PASS")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
