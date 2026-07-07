# Teensy 4.0 — real-time microcontroller

*Last updated: 2026-06-17.*

## Role
The low-level real-time controller. At **50 Hz** it: receives the `/cmd_vel` command, computes each
wheel's target speed (differential kinematics), reads the **encoders**, runs a per-wheel **PID**, sends
**PWM + direction** to the drivers, reads the **IMU**, and publishes odometry + IMU + debug topics.

## Specifications
| | |
|---|---|
| Model | Teensy 4.0 |
| MCU | NXP **IMXRT1062**, Cortex-M7 @ 600 MHz |
| Logic | **3.3 V** (⚠️ not all pins are 5 V tolerant) |
| USB | native serial (shows up as `/dev/ttyACM0`) |
| USB serial number | `16778200` |
| Firmware | `linorobot2_hardware` (PlatformIO, env `teensy40`) |

## Communication
- **To the Pi**: USB serial, **micro-ROS (XRCE-DDS)** protocol, **115200 baud**. The Teensy is the
  *client*; the *agent* runs on the Pi. (details: see the micro-ROS / networking docs in
  [`openamr-platform-sw`](https://github.com/openAMRobot/openamr-platform-sw), `docs/real_robot/`)
- **To the IMU**: I²C (SDA pin 18, SCL pin 19), address 0x68. ([imu.md](../sensors/imu.md))
- **To the encoders**: A/B quadrature on interrupts. ([encoders.md](../sensors/encoders.md))
- **To the drivers**: PWM + 2 direction lines per motor. ([motors-drivers.md](../motor_control/motors-drivers.md))

## Pinout
See the dedicated sheet **[wiring-pinout.md](../wiring/wiring-pinout.md)** (all pins in one place).

## Firmware & flashing
- Source and structure: **firmware/firmware.md (see `openamr-platform-fw`: Teensy 4.0 overlay README)**.
- Build/flash on the Pi: **procedures/running-the-robot.md (see `openamr-platform-sw` run-book)**.
- ⚠️ The firmware **starts on its own** at power-up (USB). There is nothing to "launch" on the Teensy;
  what you launch is the **agent** on the Pi.

## Good to know / gotchas
- The **LED (pin 13)** is a diagnostic: 3 repeated blinks = init failure (IMU not recognized, or ROS
  entity creation failed). Solid LED = connected to the agent.
- The current firmware includes **debug** additions (`/debug/*` topics) and an **open-loop mode**
  (`/debug/openloop`) to test the motors without the PID. See firmware/debug-telemetry.md (see `openamr-platform-fw`: Teensy 4.0 overlay README).
- You **cannot read back** the flashed firmware (the Teensy can't be dumped): the only "backup" is the
  source code in `~/linorobot2_hardware`.
