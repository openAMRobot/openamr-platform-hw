# Changelog

All notable changes to this repository are documented here. Dates are ISO-8601.

## [Unreleased]

### Added
- Real-robot audit findings integrated into the hardware docs: Pi 5 thermal throttling
  (no cooler, 83 °C) + 5 V/5 A bring-up brown-out; ZBLD motor-driver LED fault-code reference;
  encoder velocity-error profile; measured velocity floors; DC power wire colours; battery
  voltage thresholds.
- `LICENSE` (MIT for docs, (c) 2026 OpenAMRobot), `NOTICE.md`, `AUTHORS.md`, `SECURITY.md`,
  `CONTRIBUTING.md` (were empty).

### Fixed
- Drivetrain dimensions in the BOM: corrected the wheel size to the firmware-measured
  ⌀ 0.2 m / track 0.46 m and removed an incorrect "measured 0.046533 m radius" that was a
  CAD-export artifact (axle height), with a note flagging the matching sim (`robot.sdf`) bug.

### To do before release
- Populate or clearly scope the empty `mechanical/`, CAD, and PCB directories.
- Physically verify the track (tape measure) to reconcile firmware 0.46 m vs CAD 0.4075 m.
