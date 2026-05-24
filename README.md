# OpenAMR Platform Hardware

Mechanical, electrical, CAD, BOM, chassis, and mechatronics repository for the OpenAMR mobile robot platform.

## Repository Status

> The latest HW and FW information is currently available in the [openAMR](https://github.com/openAMRobot/openamr) repository. The OpenAMR HW content will be migrated to this repository shortly.

Current maturity level: Experimental

## Purpose

This repository contains hardware-related resources for the OpenAMR mobile robot platform, including:

- chassis design
- CAD files
- mechanical drawings
- renderings
- electrical architecture
- power distribution
- motor control wiring
- sensor placement
- computing hardware integration
- PCB files
- BOM lists
- vendor information
- assembly documentation
- safety documentation

## Repository Structure

```text
openamr-platform-hw/
├── mechanical/
├── electrical/
├── manufacturing/
├── interfaces/
├── assets/
└── docs/
```

## Repository Boundaries

This repository contains hardware and mechatronics files.

Software belongs in:

```text
openamr-platform-sw
```

Firmware belongs in:

```text
openamr-platform-fw
```

User-facing documentation belongs in:

```text
openamrobot-docs
```

## Safety Notice

Hardware work can involve mechanical hazards, electrical hazards, batteries, motors, moving parts, and manufacturing risks.

Users are responsible for validating:

- mechanical safety
- electrical safety
- battery safety
- wiring correctness
- manufacturing quality
- regulatory compliance
- deployment suitability

## License

License terms will be defined per asset type.

Recommended future direction:

- hardware design files: CERN-OHL-S-2.0
- documentation: MIT or Creative Commons
- branding assets: reserved
