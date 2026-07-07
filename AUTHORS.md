# Authors and Contributors

This repository is maintained by the OpenAMRobot organization.

## Maintainer

- OpenAMRobot organization
- Contact: botshare.ai@gmail.com

## Contributors

Recognition is given to contributors whose work has materially shaped this repository.
Listing here does not replace GitHub history — it complements it.

### Hardware documentation, real-robot findings, and diagrams

- **Matthieu Vinet** — [@SHuttooo](https://github.com/SHuttooo)
  - **Electrical documentation** for the real robot: the Teensy 4.0 wiring & pinout, the ZBLD
    motor-driver wiring and DIP configuration, power distribution & electrical safety, and the
    sensor notes (AS5040 encoders, MPU6500 IMU, RPLIDAR, camera) and computing notes (Pi 5,
    Teensy 4.0).
  - **Bill of materials** (`manufacturing/bom/`) with the measured drivetrain constants.
  - **Real-robot audit findings** integrated into the docs:
    - Pi 5 thermal throttling (no cooler, ~83 °C) and the 5 V/5 A bring-up brown-out.
    - The **ZBLD LED fault-code reference**.
    - The **AS5040 5 V → 3.3 V overvoltage fix** (A/B outputs over-driving the non-5 V-tolerant
      Teensy inputs).
    - Encoder velocity-error profile, measured velocity floors, DC wire colours, and the
      24 V lead-acid battery voltage thresholds.
    - Corrected drivetrain dimensions (wheel ⌀ 0.2 m / track 0.46 m, firmware-measured).
  - **Wiring & schematic diagrams**: the system harness, Teensy pin map, ZBLD driver
    connections, DIP switches, power distribution, motor signal chain, and encoder wiring.
  - **Licensing** and repository meta (`LICENSE`, `NOTICE`, `SECURITY`, `CONTRIBUTING`).

### Repository scaffolding

- **Alex** ([OpenAMRobot maintainer](mailto:botshare.ai@gmail.com))
  - Initial `openamr-platform-hw` repository structure and governance scaffolding.
