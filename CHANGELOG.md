# Changelog

All notable changes to this repository are documented here. Dates are ISO-8601.

## [Unreleased]

### Changed
- CAD Rev B for the OpenAMRobot 2.0 sensor set (P-03 rev19.0 item 19); the previous CAD is kept
  in release v0.0.1.
  - Front and back panels (`MMP.00.00.00.001`, `MMP.00.00.00.002`): MB7060 holes at the panel
    edges (y ±130 mm, 91.4 mm above the floor), TF-Luna openings on the centreline (front and a
    new rear opening). Front panel: Gemini 336L opening 126 x 36 mm with four ⌀5.6 holes for M4
    inserts. The ⌀22.5 E-stop and push-button holes are kept.
  - New STEP and DXF for both panels; the native SLDPRT and SLDDRW files are removed for now.
    The PDF drawings are still Rev A.
- Full assembly: 4 x MB7060, 2 x TF-Luna, Gemini 336L 10° up on the camera mount, RPLIDAR S3 on
  the 17.5 mm spacer, electronics bracket with the Jetson, STM32 and IMU, ZLAC8015D motor driver
  and the battery cells. Stored as `MMP.00.00.00.000_full_assembly.STEP.zip` (139 MB STEP, 25 MB
  zip), because GitHub rejects files over 100 MB.
- LiDAR stack: MMP.07 bracket + 17.5 mm printed spacer MMP.07.00.00.002, no standoffs. The S3
  beam is 174.0 + 17.5 + 30.55 = 222.05 mm above the floor (was a 7.1 mm plate on the 10 mm
  standoffs, BOM Issue 7.7 MEC-008).

### Added
- 3D-printed parts (PETG, STEP and STL): MMP.01.00.00.003 Camera mount (10°),
  MMP.00.00.00.005 TF-Luna mount (x2), MMP.00.00.00.006 Ultrasonic mount (x4),
  MMP.07.00.00.002 LiDAR mount spacer (17.5 mm), MMP.02.00.00.002 Motor driver mount.
  Listed in `manufacturing/bom/mechanical-bom.md`.
- MMP.04.00.00.002 Electronics bracket (2 mm sheet, under and in front of the center bracket;
  carries the Jetson and the IMU) and MMP.04.00.00.003 STM32 Click mount plate (6 mm), STEP.
  IMU ICM-42688-P on the centreline, 54.4 mm in front of the drive axle, 177 mm above the base
  plate.
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
- CAD Rev B open items:
  - Base plate: to be discussed (motor driver holes and further changes).
  - Electronics bracket MMP.04.00.00.002 needs approval.
  - Motors will change when the new motor CAD arrives.
  - Many mounting fasteners are missing (heat-set inserts, spacers, screws); they will be added
    after the SW (robot model) update, with exact lengths in the drawings and
    `manufacturing/bom/mechanical-bom.md`.
  - MB7060 holes are ⌀29.46; P-03 rev19.0 item 19 asks for ⌀27.5 (3/4 in NPS lock nut).
  - TF-Luna openings are 30 x 23 mm; P-03 rev19.0 item 19 asks for ⌀22 holes. The TF-Luna mount
    face is 10°; the screening value is 20° down.
  - Camera opening centre is 144.3 mm above the floor and 0.37 mm off the centreline; the
    decision is 142.5 mm on the centreline. The camera mount part still has ⌀4.7 holes.
  - Electronics bracket bend radius is R2.0; the repository rule for 2 mm sheet is R2.4 (K 0.47).
    Flat-pattern DXFs are missing (the panel DXFs are face outlines, none yet for the
    electronics bracket); they will follow after the SW push.
  - Battery pack (8 cells) is placed only and not fixed; the fixing waits for the BMS CAD.
    Base plate holes for the motor driver are not all added yet.
  - Panel PDF drawings are still Rev A.
- Populate or clearly scope the empty `mechanical/`, CAD, and PCB directories.
- Physically verify the track (tape measure) to reconcile firmware 0.46 m vs CAD 0.4075 m.
