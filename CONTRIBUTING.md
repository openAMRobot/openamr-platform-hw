# Contributing to OpenAMRobot Platform Hardware

Thank you for your interest in contributing to `openamr-platform-hw`.

This repository contains the **hardware documentation** for the OpenAMRobot mobile base:
electrical wiring/pinouts, power distribution, sensor and motor-control notes, the BOM, and
safety documentation. It is documentation-first; CAD/PCB directories are placeholders.

## Licensing of contributions

- Documentation and BOM contributions are accepted under **MIT** (`LICENSE`), (c) OpenAMRobot.
- Future hardware design files (CAD/schematics/PCB) will be **CERN-OHL-S-2.0**; do not add
  design files until that carve-out is in place.
- Do not add third-party datasheets/design files unless their license permits redistribution.

## Ways to contribute

- correct or extend wiring/pinout, power, and motor-control docs (cite how you verified)
- keep the BOM accurate (part numbers, quantities, measured values)
- document safety gaps and known limitations honestly

## Guidelines specific to hardware docs

- **Safety-relevant values must be verified**, not guessed. If a value is derived or unverified,
  say so and how to confirm it (e.g. "measure with a multimeter / tape measure").
- Prefer measured values over datasheet-nominal where they differ; note the difference.
- Genericize deployment-specific details (hostnames, IPs, user paths) or clearly label them a
  "reference installation".

## Commit / PR

- Sign off your commits (DCO): `git commit -s`.
- One logical change per PR; state how you verified any safety-relevant value.
