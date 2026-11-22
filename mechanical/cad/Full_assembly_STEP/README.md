# Full assembly (STEP)

`MMP.00.00.00.000_full_assembly.STEP.zip` holds the complete mobile-base assembly as one STEP file, exported from Fusion. The current file is the 22 November 2026 export.

## Status

This is a draft layout. It includes the reworked rear power layout (GI-080) and the front electronics placement.

- Parts with no selected model or no vendor CAD yet are simple boxes. Their names end in `(envelope)`.
- Fuse ratings and cable sizes are not approved for wiring release.

## Third-party models

The assembly includes vendor CAD models for fit and clearance checks. They belong to their respective owners. The OpenAMRobot hardware licence (CERN-OHL-P-2.0) does not cover them, and their own terms of use apply. Vendor models in this assembly include:

- ZLTech ZLLG80ASM250 hub motors and ZLAC8015D driver
- Blickle LPA-VSTH 35K castors
- DOLD Hexalift EB530 lift column
- Blue Sea Systems 5046, 7748, 2307 and 6004
- Sensata Gigavac GX11 contactors
- MEAN WELL DDR-240B-24 and RSD-60G
- StarTech ST7300USBME USB hub
- Orbbec Gemini 336L
- Slamtec RPLIDAR S3
- Benewake TF-Luna
- MaxBotix HRXL-MaxSonar-WR
- Seeed reComputer Robotics J401
- STMicroelectronics NUCLEO board
- MikroE Click Shield and CAN Isolator 3 Click
- Waveshare SN65HVD230 CAN board
- Rexnord UCFL bearings
- EMAS push buttons
- Standard DIN and ISO fasteners

The OpenArm arms are not included. Their CAD is in [enactic/openarm_hardware](https://github.com/enactic/openarm_hardware) under CERN-OHL-S-2.0, and this repository links to it rather than copying it.
