# Near-field sensors: MaxBotix MB7060 ultrasonic and Benewake TF-Luna cliff sensors (2.0)

*Last updated: 2026-10-12.*

Source: P-03 Decision Addendum rev19.0 item 19 (12 Oct 2026) and BOM Issue 7.7; geometry from STEP
MMP.00.00.00.000.

**Functional sensing only: the near-field sensors are not a safety device.** They feed obstacle and
cliff detection; they do not implement or validate any safety function.

## Ultrasonic: 4 × MaxBotix MB7060 XL-MaxSonar-WR

| | |
|---|---|
| Model | **MaxBotix MB7060 XL-MaxSonar-WR**, **-2XX** 3/4 inch NPS housing, **RS232** output |
| Quantity | **4**: front panel left and right, back panel left and right |
| Holes | the front and back panel **left and right edge holes**, enlarged from **18.5 / 19.0 mm** to **27.5 mm** on the same centres |
| Hole centres | **y ±130 mm**, **91.4 mm above the floor** |
| Fixing | sensor centred in the hole, **3/4 inch NPS lock nut** |
| Interface | **one STM32 UART per sensor**, **9600 8N1** with **receive inversion**, plus **one trigger GPIO** per sensor |
| Tilt | **0** until the bench test |

## Cliff: 2 × Benewake TF-Luna

| | |
|---|---|
| Model | **Benewake TF-Luna** ToF |
| Quantity | **2**: front and rear |
| Holes | the existing **22.0 mm front centre hole** and a **new 22.0 mm rear centre hole** |
| Interface | **one UART per sensor**, **pin 5 tied to 3.3 V** |
| Pitch | pitched down; **20 degrees is a screening value until the bench test** |

## Frames
All frames are from `base_link` (drive-axle midpoint, 98.0 mm above the floor), in metres.

| Frame | x | y | z | yaw |
|---|---|---|---|---|
| `us_front_left` | 0.390 | 0.130 | -0.0066 | 0 |
| `us_front_right` | 0.390 | -0.130 | -0.0066 | 0 |
| `us_rear_left` | -0.390 | 0.130 | -0.0066 | π |
| `us_rear_right` | -0.390 | -0.130 | -0.0066 | π |
| `tof_front` | 0.390 | 0 | -0.0066 | 0 |
| `tof_rear` | -0.390 | 0 | -0.0066 | π |

z -0.0066 m from `base_link` is 91.4 mm above the floor. The ToF frames carry the downward pitch above
(20 degree screening value until the bench test).

## Panels
Rev B front and back panels: Cuma.

## Not verified
- The 27.5 mm holes, the new rear centre hole and the Rev B panels are not yet made.
- The ultrasonic tilt (0) and the ToF pitch (20 degrees) are screening values until the bench test.
