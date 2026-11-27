# Full assembly (STEP)

`MMP.00.00.00.000_full_assembly.STEP.zip` holds the complete robot assembly as one STEP file, exported from Fusion. The current file is the 27 November 2026 export (Fusion full assembly rev2 v94).

## Status

This is a draft layout. Compared with the 24 November export it adds the upper body and the corrections below.

- **Upper body:** lift interface (MEC-019, MEC-022, MEC-004 rev F), lift box MEC-024 rev K with cover MEC-025 rev D and chain bracket UPR-J02 rev E (release R8), junction box UPR-J01, screen pocket UI-003/UI-004, light AUX-002, chest camera mount ARM-012 (draft), energy chain.
- **Simplified configuration:** one contactor (K1), one ZED Mini (chest). KCHG, wireless charging and the external lift sensors are not in the model.
- **Corrections:**
  - The base floor is 2.0 mm, top face 54.0 mm above the floor (issue #43).
  - The arch-wall screws are M5.
  - Hole E in MEC-004 is removed.
  - The electronics plate has corner reliefs for the new-build wheel bracket B1, clearance notches for the front castor screws and 4 x M4 fixings to the base (new M4 rivet nuts in the base).
- **Placeholders:** parts with no selected model or no vendor CAD yet are simple boxes. Their names end in `(envelope)`.
- **Electrical:** fuse ratings and cable sizes are not approved for wiring release.

## Third-party models

The assembly includes vendor CAD models for fit and clearance checks. They belong to their respective owners. The OpenAMRobot hardware licence (CERN-OHL-P-2.0) does not cover them, and their own terms of use apply. Vendor models in this assembly include:

- ZLTech ZLLG80ASM250 hub motors and ZLAC8015D driver
- Blickle LPA-VSTH 35K castors
- DOLD Hexalift EB530 lift column
- Blue Sea Systems 5046, 7748, 2307 and 6004
- Sensata Gigavac GX11 contactor
- MEAN WELL DDR-240B-24 and RSD-60G
- StarTech ST7300USBME USB hub
- Orbbec Gemini 336L
- Stereolabs ZED Mini
- Slamtec RPLIDAR S3
- Benewake TF-Luna
- MaxBotix HRXL-MaxSonar-WR
- Seeed reComputer Robotics J401
- STMicroelectronics NUCLEO boards
- MikroE Click Shield and CAN Isolator 3 Click
- Waveshare SN65HVD230 CAN board
- Pololu D24V50F5 regulator
- WAGO 221-415 lever terminals
- igus E2/000 1500.068.075.0 energy chain
- Schneider Electric XB4BS emergency stop
- TDK InvenSense ICM-42688-P evaluation board
- Daly BMS
- FLDL-i150X15 light bar
- Rexnord UCFL bearings
- EMAS push buttons
- Standard DIN and ISO fasteners

The OpenArm arms are not included. Their CAD is in [enactic/openarm_hardware](https://github.com/enactic/openarm_hardware) under CERN-OHL-S-2.0, and this repository links to it rather than copying it.
