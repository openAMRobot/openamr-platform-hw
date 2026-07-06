# Motor driver fault codes — ZBLD.C20-120L2R

*How to read the driver's LED blink code and the full fault-code table. Driver: **ZBLD.C20-120L2R**
(Ningbo Zhongda Leader / ZD), 24 V ±20 %, 7.5 A, 120 W. One per wheel (LEFT = M1, RIGHT = M2).*

*Last updated: 2026-06-26.*

> When a driver detects a fault it **STOPS the motor** and blinks an error code on its LEDs. So a red LED
> is not cosmetic — the motor will not turn until the fault is cleared, even though the Teensy keeps
> sending PWM (you can confirm the Teensy side is fine: `/debug/pwm` still shows the commanded value).

## Reading the LED blink code

Each driver has a **green** and a **red** indicator. On a fault they flash a repeating pattern:

```
ERROR CODE = (number of GREEN flashes × 5) + (number of RED flashes)
```

Count one full cycle: the **green** flashes first (each green = 5), then the **red** flashes (each red = 1),
then it repeats. **Count green and red separately** — do NOT add them into one running count.

> ⚠️ **The encoding is NOT a clean base-5 code, so `green×5 + red` can alias** (e.g. 1 green + 5 red and
> 2 green + 0 red both arithmetic to 10). Do not "carry" a 5th red into an extra green — read the *actual
> emitted pattern* the driver blinks. Below are the patterns **observed on this robot** (field-confirmed);
> for any code not seen here, read the pattern off the driver and cross-check the fault-code table.

| You see (emitted pattern) | Code | Meaning | Confirmed |
|---|---|---|---|
| **1 green, 5 red** | **10** | busbar under-voltage | ✅ seen on this robot (2026-06-26) |
| **2 green, 4 red** | **14** | locked rotor | ✅ seen on this robot (2026-07-01, wheel jammed on wall) |

*(Other codes in the fault-code table below are from the manufacturer manual and have not been observed
here — read the blink pattern off the driver, then look up the code. Green contributes 5 each, red 1 each,
but trust the pattern the driver actually shows, not a computed sum.)*

## Fault-code table

| Code | Fault | Typical cause |
|---|---|---|
| **1–6** | **Over-current** (during acceleration / deceleration / constant speed) | short on the motor phases, motor stalled/jammed, wrong wiring, current limit too low |
| **7–9** | **Over-voltage** (different operating phases) | supply > 28.8 V, or regenerative braking spikes (decel) with no bleed |
| **10** | **Busbar under-voltage** | **24 V too low**: flat/weak battery, voltage drop under load, supply can't hold the current spike at fast acceleration, or driver HW fault |
| **11** | **Motor overload** | motor drawing too much for too long (load too high, gearbox binding) |
| **12** | **Driver overload** | driver output beyond its rating (7.5 A / 120 W) |
| **13** | **Hall sensor error** | Hall connector loose/miswired/disconnected → driver can't commutate |
| **14** | **Locked rotor** | motor blocked / can't turn (mechanical jam, brake on) |
| **16** | **Driver over-temperature** | heatsink too hot — sustained high load / poor cooling |
| **19** | Current sense error | internal current-measurement fault |
| **27** | Data storage error | driver parameter/EEPROM error |
| **29** | Over-current feedback error | current-feedback path fault |
| **30** | **Lack of input phase** | a motor phase (U / V / W) is missing — phase wire disconnected |

*(Codes grouped 1–6 / 7–9 cover the same fault type at different motion phases; exact sub-code detail is
in the manufacturer's manual, [ZBLD.C20.pdf](https://image.yhdfa.com/Uploads/Picture/PDF/FZ02_11/ZBLD.C20.pdf).)*

## Clearing a fault
1. **Fix the cause first** (see the table — e.g. for code 10, recharge the battery to ≥ 25 V).
2. **Power-cycle the 24 V** (cut, wait a few seconds, restore). Faults **latch** until a power cycle.
3. The red LED should go out and the motor respond again.

## Most common on this robot — code 10 (under-voltage)
**Both drivers showing code 10 at once = a shared cause = the 24 V bus is too low** (they share one
battery). The ZBLD.C20 needs **24 V ±20 % (≈ 19.2–28.8 V)**; below that → under-voltage → both stop.
- Diagnosis: measure the battery at rest — if **< ~22 V** (let alone < 19 V), that's it.
- Note: a *charged but weak* battery can still trip code 10 **under load** ("voltage drop / fast
  acceleration") — the pack sags at the current spike. Same root as the Pi 5 brown-outs
  ([raspberry-pi.md](../computing/raspberry-pi.md) / [power.md](../power_distribution/power.md)): keep the
  battery healthy + ≥ 25 V, with short, thick 24 V wiring.
- Fix: **charge to ≥ 25 V → power-cycle the 24 V → red LED off → wheels turn** (`ros2 topic pub --rate 15
  /debug/openloop geometry_msgs/msg/Vector3 "{x: 100.0}"` with the robot lifted).

## If it is NOT under-voltage (battery confirmed good)
- **Code 13 (Hall error) / 30 (missing phase)** → a motor connector is loose/disconnected (check the
  Hall and U/V/W wiring; brown = +, blue = − for power leads).
- **Code 1–6 (over-current) / 14 (locked rotor)** → the motor is jammed or shorted — check the wheel
  turns freely and the phase wiring isn't shorted.
- **Code 16 (over-temp)** → let it cool; reduce sustained load.

See also: [motors-drivers.md](motors-drivers.md) (driver model, DIP switches, pots),
[power.md](../power_distribution/power.md) (battery / 24 V), and the `openamr-platform-sw`
troubleshooting doc (`docs/troubleshooting/diagnostics.md` in that repo).
