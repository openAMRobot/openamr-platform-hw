# Wiring & Teensy 4.0 pinout

*Last updated: 2026-06-19.*

Convention: **MOTOR1 = LEFT wheel, MOTOR2 = RIGHT wheel.** Logic level **3.3 V**.

> **Verification status (2026-06-19):** full wiring/component audit done. Physically verified —
> **drivers + motors** (ZBLD C20-120L2R + ZD Z4BLD60-24GN-30S, both drivers identical), **encoders**
> (AS5040; the 5 V→~4 V overvoltage was **fixed → now 3.3 V**, see [encoders.md](../sensors/encoders.md)), **IMU**
> (MPU-6500, SDA18/SCL19, 3.3 V, 0x68), **Teensy = 4.0** (i.MX RT1062), **power/24 V** (no fuse / no
> battery cut-off — see [power.md](../power_distribution/power.md)). Component list + datasheets: [components-bom.md](../../manufacturing/bom/components-bom.md).
> Still to read (completeness): LiDAR model sticker, DC-DC model, AC/DC converter, gearbox suffix.
> (Pi RAM confirmed **8 GB**, 2026-07-06 — see [raspberry-pi.md](../computing/raspberry-pi.md).)

The complete power-and-signal wiring is shown in the harness diagram below; the sections that
follow give the exact pin/terminal tables behind it.

> ### 📐 Diagram: Wiring harness (system overview)
> *Figure 1 — the full OpenAMRobot wiring harness: power (24 V) and logic (3.3 V) domains, and every signal link.*
>
> **Prompt to generate this diagram (paste to Claude):**
> ```
> Create a clean labeled wiring/harness block diagram for a differential-drive robot. Show these blocks and every connection between them, keeping the 24 V POWER domain visually separate (e.g. red/thick) from the 3.3 V LOGIC domain (e.g. blue/thin):
> - 24 V lead-acid battery (2x 12 V in series) -> [MISSING: fuse] -> 24 V bus.
> - 24 V bus -> two ZBLD.C20-120L2R motor drivers (V+/V-).
> - 24 V bus -> DC-DC buck -> 5 V -> Raspberry Pi 5.
> - Each driver -> its ZD Z4BLD60 BLDC motor: 3 phases U/V/W + 3 Hall sensors Hu/Hv/Hw + Hall Vcc(5V)/0V.
> - Teensy 4.0 (3.3 V logic) signal links: to LEFT driver PWM=pin1, FWD=pin20, REV=pin21; to RIGHT driver PWM=pin5, FWD=pin6, REV=pin8; each driver COM tied to Teensy GND (common ground, mandatory).
> - AS5040 encoders (3.3 V): LEFT A/B -> Teensy pins 14/15; RIGHT A/B -> pins 11/12.
> - MPU6500 IMU (3.3 V, I2C 0x68): SDA->pin18, SCL->pin19.
> - Raspberry Pi 5 <-> Teensy over USB (micro-ROS, 115200); Pi <-> RPLIDAR A1 over USB; Pi <-> Camera Module 3 over CSI.
> Label voltages on every rail. Mark the missing fuse and missing battery disconnect as red 'NOT FITTED' notes.
> ```

## Teensy 4.0 pin assignment

| Function | Pin | Notes |
|---|---|---|
| **IMU** SDA | 18 | I²C data (MPU6500 @ 0x68) |
| **IMU** SCL | 19 | I²C clock |
| **Encoder LEFT (M1)** A | 14 | quadrature |
| **Encoder LEFT (M1)** B | 15 | quadrature |
| **Encoder RIGHT (M2)** A | 11 | quadrature |
| **Encoder RIGHT (M2)** B | 12 | quadrature |
| **Motor LEFT (M1)** PWM | 1 | → driver `VAR/AI2` (speed) |
| **Motor LEFT (M1)** IN_A / FWD | 20 | → driver `FWD/DI1` |
| **Motor LEFT (M1)** IN_B / REV | 21 | → driver `REV/DI2` |
| **Motor RIGHT (M2)** PWM | 5 | → driver `VAR/AI2` (speed) |
| **Motor RIGHT (M2)** IN_A / FWD | 6 | → driver `FWD/DI1` |
| **Motor RIGHT (M2)** IN_B / REV | 8 | → driver `REV/DI2` |
| Debug LED | 13 | init/status (3 blinks = init failure) |
| micro-ROS | USB | native serial, 115200 baud |

> These values are also the `#define`s in `lino_base_config.h` (see the `openamr-platform-fw` overlay README (`boards/teensy_4_0/linorobot2_overlay/README.md`)).
> Note: `MOTOR1_PWM` is pin **1** (pin 21 is **not** a PWM pin on the Teensy 4.x — a common upstream pitfall).

The same assignment is shown as a physical pin map below.

> ### 📐 Diagram: Teensy 4.0 pin map
> *Figure 2 — the Teensy 4.0 board with each used pin labeled by function.*
>
> **Prompt to generate this diagram (paste to Claude):**
> ```
> Draw a top-view pinout diagram of a PJRC Teensy 4.0 board (two rows of pins). Label ONLY the pins used by this robot, colour-grouped by function:
> - I2C (IMU): pin 18 = SDA, pin 19 = SCL.
> - Encoders (quadrature): pin 14 = LEFT A, 15 = LEFT B, 11 = RIGHT A, 12 = RIGHT B.
> - Motor LEFT: pin 1 = PWM (only PWM-capable pin used), 20 = FWD, 21 = REV.
> - Motor RIGHT: pin 5 = PWM, 6 = FWD, 8 = REV.
> - Pin 13 = debug LED. USB = micro-ROS serial (115200).
> Add a callout: 'pin 21 is NOT PWM-capable on Teensy 4.x — that is why MOTOR1 PWM is pin 1'. All I/O is 3.3 V, NOT 5 V tolerant — add that as a warning banner.
> ```


## Driver wiring — ZBLD C20-120L2R (VERIFIED 2026-06-19)

Both drivers are wired **identically** (only the Teensy pins differ). The signal terminal block has 12
positions; **exactly 4 are connected** per driver (read off the board: `x`=wired, `o`=empty, from FWD):

```
FWD/DI1  REV/DI2  JOG/DI3  CLR/DI4  BRK/DI5  COM  VAR/AI2  +5V  ERR/DO1  SPD/DO2  A+  B-
   x        x        o        o        o      x      x      o      o        o     o   (o)
```

| Driver terminal | Role | ← Teensy LEFT (M1) | ← Teensy RIGHT (M2) |
|---|---|---|---|
| `VAR/AI2` | speed setpoint, analog **0–5 V** (Teensy PWM @3 kHz, filtered) | PWM **1** | PWM **5** |
| `FWD/DI1` | forward direction (digital) | IN_A **20** | IN_A **6** |
| `REV/DI2` | reverse direction (digital) | IN_B **21** | IN_B **8** |
| `COM` | **common ground — mandatory** | GND | GND |

The driver's connected terminals and their Teensy links are shown below.

> ### 📐 Diagram: Driver signal + power connections (ZBLD C20-120L2R)
> *Figure 3 — one ZBLD driver: which of its 12 signal terminals are wired, plus the 24 V power and motor connector.*
>
> **Prompt to generate this diagram (paste to Claude):**
> ```
> Draw a connection diagram for one ZBLD.C20-120L2R BLDC driver. Show its 12-position signal terminal block with ONLY these 4 wired (others greyed 'not connected'): VAR/AI2 (speed, analog 0-5 V from a filtered Teensy PWM), FWD/DI1 (forward, digital), REV/DI2 (reverse, digital), COM (common ground). Show the incoming Teensy links (PWM, FWD, REV, GND). Separately show the 24 V DC power screw terminals (V+/V-, brown=+, blue=-) and the 8-pin Molex motor connector (U, V, W phases + Hu, Hv, Hw Halls + Vcc 5 V + 0V). Note: the driver does its own commutation from the Halls; the Teensy never sees U/V/W.
> ```


Unused: `JOG/DI3`, `CLR/DI4`, `BRK/DI5` (brake), `+5V`, `ERR/DO1` (no fault read-back), `SPD/DO2`
(no speed feedback to the Teensy), `A+/B−` (RS485 not used). Speed/gain is set by the on-board **VAR/AI1**
pot + **ACC/DEC** ramp pot (see [motors-drivers.md](../motor_control/motors-drivers.md)).

> ⚠️ The Teensy uses the `USE_GENERIC_2_IN_MOTOR_DRIVER` profile (PWM + INA + INB). On this BLDC driver
> that maps cleanly: PWM→speed (`VAR/AI2`), INA→`FWD/DI1`, INB→`REV/DI2`. The driver does its own
> commutation from the Hall sensors — the Teensy never sees U/V/W.

### DIP switches (config applied 2026-06-19, identical both drivers)
| SW1 | SW2 | SW3 | SW4 | SW5 | SW6 |
|---|---|---|---|---|---|
| **OFF** | **ON** | OFF | **ON** | **ON** | OFF |

The switch positions are shown below.

> ### 📐 Diagram: Driver DIP switch settings
> *Figure 4 — the 6-position DIP block on each driver, drawn in the applied configuration.*
>
> **Prompt to generate this diagram (paste to Claude):**
> ```
> Draw a 6-position DIP switch block (SW1..SW6) in this exact state: SW1=OFF, SW2=ON, SW3=OFF, SW4=ON, SW5=ON, SW6=OFF. Annotate each: SW1=OFF -> open loop (Teensy PID is the sole regulator); SW2=ON -> speed source = AI2 (external 0-5 V PWM input); SW3=OFF; SW4=ON & SW5=ON -> 5 pole pairs (motor P=5); SW6=OFF -> no RS485. Both drivers are set identically.
> ```


- **SW1 = OFF → open loop** (driver is a power stage; the **Teensy PID** is the sole regulator — best
  for this robot, removes the double loop). *Was ON (closed loop); changed 2026-06-19.* Validated: smooth.
- **SW2 = ON → speed source = AI2** (the external 0–5 V input where our PWM arrives). Must stay ON.
- **SW4 = ON, SW5 = ON → 5 pole pairs** (motor is P=5). *Was OFF/OFF (=2 pp, wrong); corrected.*
  Irrelevant in open loop but set correctly for future closed-loop use.
- **SW6 = OFF** (no RS485). See the full rationale in [motors-drivers.md](../motor_control/motors-drivers.md).
- ⚠️ With SW2=ON (AI2 source), the **VAR pot is inert** for balancing — speed comes from the PWM, not the
  pot. The residual ~9 % open-loop L/R asymmetry is handled by the Teensy PID (→ ~0.2 %).

## Motor wiring (per motor) — VERIFIED 2026-06-19
Driver **power**: `V+ / V− = 24 V DC` (大 screw terminals, bottom-right, `电源DC24V`), fused.

> ⚠️ **DC power wire colours on THIS robot** (confirmed 2026-06-18, counter-intuitive — AC-style colours on
> a DC bus): **brown = + (V+, i.e. the DC "red")**, **blue = − (V−, i.e. the DC "black")**. Colour is only a
> presumption — **verify with a multimeter** before connecting a 24 V lead. See [power.md](../power_distribution/power.md).

Driver **motor connector** (white Molex, 8 pins):

| `U` | `V` | `W` | `Hu` | `Hv` | `Hw` | `Vcc` | `0V` |
|---|---|---|---|---|---|---|---|
| phase U | phase V | phase W | Hall U | Hall V | Hall W | +5 V (Hall supply) | GND (Hall) |

> 🔧 **Left-wheel blocker:** the left signal wiring (4 terminals above) is **proven healthy**, so the
> intermittent left wheel is NOT here — it's on the **24 V power (V+/V−)** or the **motor connector**
> (a phase or the Molex). That's where to chase the faux-contact (continuity test while flexing). See
> the `openamr-platform-sw` troubleshooting doc (`docs/troubleshooting/diagnostics.md` in that repo) and the `amr-left-wheel-faux-contact` memo.

## Grounding
All grounds must be common: **Teensy GND ↔ driver COM**. A floating COM was a real source of noise
concern (see the `openamr-platform-sw` troubleshooting doc (`docs/troubleshooting/diagnostics.md` in that repo)).

## ASCII map
```
                 Teensy 4.0 (3.3V)
   IMU  ── SDA18/SCL19 ───────────────► MPU6500 (I2C 0x68)
   ENC L ── A14/B15 ──────────────────► encoder LEFT
   ENC R ── A11/B12 ──────────────────► encoder RIGHT
   M1   ── PWM1 / IN20 / IN21 ────────► driver LEFT  ── U/V/W ─► motor LEFT
   M2   ── PWM5 / IN6 / IN8 ──────────► driver RIGHT ── U/V/W ─► motor RIGHT
   USB ───────────────────────────────► Raspberry Pi (micro-ROS 115200)
   GND ───────────────────────────────► COM of both drivers (common)
```
