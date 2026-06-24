# Components — Bill of Materials & datasheets

*Last updated: 2026-06-19.* Identification done by reading the real labels on the robot + manufacturer
datasheets. Status: ✅ = confirmed (label + datasheet), ⏳ = to read the exact label/marking.

| # | Component | Exact name / part number | Status | Datasheet / source |
|---|---|---|---|---|
| 1 | Microcontroller | **Teensy 4.0** (MCU NXP **i.MX RT1062**, Cortex-M7 600 MHz) | ✅ | [pjrc.com/store/teensy40](https://www.pjrc.com/store/teensy40.html) |
| 2 | Motor drivers ×2 | **ZBLD.C20-120L2R** (Ningbo Zhongda Leader / ZD) | ✅ | [manual V1.02 (PDF)](https://image.yhdfa.com/Uploads/Picture/PDF/FZ02_11/ZBLD.C20.pdf) · [product](https://www.zd-motor.com/product/ZBLD.C20-120L2R-64.html) |
| 3 | Motors ×2 | **Z4BLD60-24GN-30S** (ZD geared BLDC, 60 W / 24 V / 3.8 A / 3000 rpm / **P=5**) | ✅ nameplate | [analog F5B60-24GN-30S spec](https://www.omc-stepperonline.com/24v-60w-100rpm-geared-brushless-dc-motor-4-18nm-591-94oz-in-30-1-spur-gearbox-f5b60-24gn-30s-5gn30k) · [ZD](https://en.zd-motor.com/) |
| 4 | Encoders ×2 | **AMS AS5040** (magnetic, quadrature A/B, marking "AS5040 AB 2.2") | ✅ | [AS5040 datasheet (ams, PDF)](https://www.mouser.com/datasheet/2/588/AS5040_DS000374_4_00-2066720.pdf) |
| 5 | IMU | **TDK InvenSense MPU-6500** (board silk says "MPU-6050"/GY-521, but the chip is a 6500) | ✅ | MPU-6500 datasheet (TDK/InvenSense) |
| 6 | LiDAR | **Slamtec RPLIDAR A1** (A1M8, by shape) | ⏳ confirm sticker | [slamtec.com RPLIDAR A1](https://www.slamtec.com/en/Lidar/A1) |
| 7 | Camera | **Sony IMX708** = Raspberry Pi **Camera Module 3 NoIR** | ✅ | [raspberrypi.com camera-3](https://www.raspberrypi.com/products/camera-module-3/) |
| 8 | SBC | **Raspberry Pi 5** | ✅ | confirm RAM (4/8/16 GB) |
| 9 | DC-DC 24 V→5 V | generic **~300 W 20 A CC/CV buck** (toroid + 2 trimpots) | ⏳ no clear model | (generic) |
| 10 | Battery ×4 | **DM12-7S** — 12 V **7 Ah**/20HR lead-acid (AGM) | ✅ | DM12-7S SLA datasheet (generic 12 V 7 Ah) |
| 11 | AC/DC 230→24 V | unknown | ⏳ read label | — |

## Key specs that affect configuration

### Motors — Z4BLD60-24GN-30S (ZD geared BLDC)
*Nameplate read 2026-06-19: 60 W, 24 VDC, 3000 RPM, 3.8 A, Class B Cont, IP20, **P=5**, dated 2021/07/11.*
- **3-phase, P=5 → 5 pole pairs** (confirmed on the nameplate), 24 V, **60 W**, rated current **3.8 A**.
- Motor **3000 rpm**, **spur gearbox ~30:1** (read the gearbox `4GN__K` label to confirm) → **~100 rpm
  at the wheel** (rated torque ~4.18 N·m at 30:1).
- **Hall sensors** for the driver's commutation (separate from the AS5040 encoder).
- ⚠️ **Pole pairs = 5** → check the driver **DIP SW4/SW5** are set for 5 pole pairs (read the table on
  the driver silkscreen / the manual). Currently SW4 OFF / SW5 OFF — **verify this = 5 pole pairs**.
  A wrong pole-pair setting throws off the driver's closed-loop speed scaling.
- ⚠️ **Gearbox 30:1 exists** → odometry: `COUNTS_PER_REV = 1024` must be **per wheel revolution**.
  The firmware works at wheel scale (`MOTOR_MAX_RPM 80` ≈ the ~100 rpm output; open-loop ~14 rpm at 20 %
  PWM), so the **AS5040 reads at wheel scale** (mounted on the output side / 1024 cnt = 1 wheel rev).
  **Still verify physically**: drive exactly 1 m, compare `/odom`.

### Drivers — ZBLD.C20-120L2R
- **24 V ±20 %**, output **7.5 A**, **120 W**, open/closed loop (±0.5 %), ACC/DEC 0.3–10 s, 5 DI (NPN) / 2 DO.
- Speed command: internal knob (**VAR/AI1**), external **analog 0–5/10 V**, or **PWM 0–20 kHz** → on this
  robot the Teensy PWM goes to **VAR/AI2** (SW2=ON selects AI2). See [wiring-pinout.md](../../electrical/wiring/wiring-pinout.md).

### Encoders — AMS AS5040
- 10-bit magnetic; **default incremental = 256 PPR → 1024 counts/rev** in quadrature = `COUNTS_PER_REV`. ✅
- Supply **4.5–5.5 V**, but an **internal regulator allows 3.3 V operation**. **Output high level = supply
  voltage** → powered at 5 V it drives **5 V** on A/B (the measured ~4 V overvoltage into the Teensy 4.0).
  **Fix option:** power it at **3.3 V** → 3.3 V outputs → safe (or add series R / divider). See
  [encoders.md](../../electrical/sensors/encoders.md).

### Battery — DM12-7S
- **12 V, 7 Ah** sealed lead-acid (AGM). A pair in series = **24 V 7 Ah**. Sags under load (see
  [power.md](../../electrical/power_distribution/power.md)). ⚠️ No fuse / no disconnect currently — see the safety gaps in [power.md](../../electrical/power_distribution/power.md).
  Fuse sizing: 2 motors × 3.5 A ≈ 7 A nominal + DC-DC; size a fuse around ~15–20 A (above nominal, below
  the wire/battery limit).

## Still to read off the robot
- **LiDAR**: confirm the model sticker (A1M8 vs other).
- **DC-DC buck**: any printed model / the regulator IC.
- **AC/DC 230→24 V converter**: brand + model + rating.
- **Raspberry Pi 5**: RAM variant.
- **Gearbox**: the reduction suffix on the gearbox label (`4GN__K`) to confirm 30:1.
