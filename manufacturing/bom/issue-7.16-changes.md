# BOM Issue 7.16: changes from Issue 7.15

Issue 7.16, 28 November 2026. This page is a public technical summary. It is design intent, not fabrication, wiring, commissioning or safety acceptance.

| Area | Issue 7.16 |
|---|---|
| Safety chain | The safety relay unit and the contactors are removed. Two emergency stop buttons and two normally open relays in series on the actuator bus, with a hardwired coil circuit and no controller in the chain. Precharge stays. Relay part and circuit are specified by the electrical owner and are not part of this extract |
| Buttons | LANBOO emergency stop push button; LANBOO 19 mm 2NO push button for RESET (short press: safety reset; press of 5 s: electronics reboot) |
| Power conversion | No 24 V DC-DC converters. The 5 V (RSD-60G-5) and 3.3 V supplies remain. Compute, lift, brakes and arms run from the battery side. 24 V-only small loads use wide-input versions (22.4 to 29.2 V) |
| Battery | Any 24 V class battery with its own BMS and fuse is accepted (22.4 to 29.2 V). Reference pack: 8 x EVE LF105 (8S1P) with a Daly Smart BMS 8S 100 A, common port. Batteries are not supplied with the robot |
| Charging | Manual charging through a connector on the rear panel with a 28.4 V / 20 A charger. Wireless charging is deferred to the next development cycle |
| Lift | No inductive stop sensors. Lift position comes from the lift controller. Four lift columns in the first build batch |
| LiDAR | RPLIDAR S3, four units in the first build batch |
| Drive | ZLTECH ZLLG80ASM250-L-B2 V1.01 hub motors, double shaft, rotary encoder, brake; eight motors in the first build batch |

Open items: relay part, LANBOO order codes, Daly order code, supplier confirmation of brake operation up to 28.4 V and of the encoder with the ZLAC8015D driver, arm input voltage range, lengths of cables marked MEASURE in the working harness list, fastener counts from the mechanical release.

Third-party product names identify references only.
