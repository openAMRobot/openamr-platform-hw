# Raspberry Pi 5 — main computer

*Last updated: 2026-07-06.*

## Role
The high-level "brain". Runs **ROS 2**, the micro-ROS agent (bridge to the Teensy), the USB/CSI
sensor drivers (LiDAR, camera), odometry, and later the navigation (Nav2/SLAM).

## Specifications
| | |
|---|---|
| Model | Raspberry Pi 5 Model B Rev 1.1 |
| CPU | 4× ARM Cortex-A76 **up to 2.4 GHz**, **aarch64 / ARM64** |
| RAM | **8 GB** (measured 2026-07-06: 6.4 GB free under the full stack — RAM is *not* a bottleneck) |
| Active cooler | **NONE fitted** ⚠️ → thermal throttling under the robot stack, see "Thermal" below |
| OS | Ubuntu Server **24.04 LTS** (Noble) |
| Kernel | 6.8.x-raspi |
| ROS | **ROS 2 Jazzy** (`/opt/ros/jazzy`) |
| Hostname | `BOTSHARE` *(reference installation — substitute your own)* |
| User | `botshare` *(reference installation)* (groups: `dialout`, `video`, `sudo`, …) |

> **Note (2026-07-06):** the current board is an **8 GB** Pi 5, fitted during a hardware swap on
> 2026-07-06 (the DHCP address moved to `172.17.17.64`; reach it by mDNS `botshare.local`, not a hard-coded
> IP). Earlier notes in this repo referenced a **4 GB** unit — that was the previous board.

## Communication
- **To the Teensy**: USB → `/dev/ttyACM0` (stable: `/dev/serial/by-id/usb-Teensyduino_USB_Serial_16778200-if00`).
  The Pi hosts the **micro-ROS agent** that exposes the Teensy's topics. See the micro-ROS / networking
docs in [`openamr-platform-sw`](https://github.com/openAMRobot/openamr-platform-sw) (`docs/real_robot/`).
- **To the LiDAR**: USB → `/dev/ttyUSB0` (CP2102 UART bridge).
- **To the camera**: **CSI** (ribbon cable), not USB.
- **ROS internal**: DDS = **CycloneDDS** (rmw_cyclonedds_cpp, adopted 2026-06-18 for Nav2/docking).

## Important directories (reference installation — `/home/<user>`, here `/home/botshare`)
| Directory | Contents |
|---|---|
| `~/linorobot2_ws` | the **micro-ROS agent** workspace (do NOT delete; it is the Teensy↔ROS bridge) |
| `~/linorobot2_hardware` | the Teensy **firmware source** (upstream clone + our config + debug) |
| `~/openamr-platform-sw` | OpenAMR **navigation** stack (cloned, not built yet) |
| `~/openamr_hardware_bringup_guide` | provided bring-up guide (reference) |
| `~/openamr_real_bringup.launch.py` | the **real bring-up launch** (agent+lidar+odom+TF) |
| `~/*.py` (encoder_*, powered_*, openloop_*, …) | diagnostic scripts |

## Access
SSH from the dev PC. See procedures/running-the-robot.md (see `openamr-platform-sw` run-book).
ROS 2 is sourced automatically in an interactive shell (`~/.bashrc`).
Over a **non-interactive** SSH command you must source it manually:
```bash
source /opt/ros/jazzy/setup.bash && source ~/linorobot2_ws/install/setup.bash
```

## ⚠️ Thermal — no active cooler → the Pi throttles navigation (2026-07-06)
The Pi 5 is fitted with **no fan / no active cooler**. Under the full robot stack it overheats and the
firmware **clock-limits the CPU**, which slows navigation planning/costmaps.

Measured live under load (2026-07-06):
- **83.4 °C** core temperature (`vcgencmd measure_temp`), approaching the 85 °C hard limit.
- **`vcgencmd get_throttled` = `0x80008`** → **soft thermal limit ACTIVELY engaged** (bit 3) **and**
  has-occurred (bit 19). **No under-voltage bits set** — the *power* rail is fine; this is purely heat.
- At 83 °C the Pi 5 caps its clock (~**2.1 GHz** vs the 2.4 GHz max) to stay under 85 °C → the Nav2
  planner/controller and costmap updates slow down. **It is not a software bug — the CPU is being
  clock-limited by heat.**

Contributing load (work navigation does not need): `dock_trigger.py` ~36 % + `camera_node` ~19 % +
`apriltag_gate.py` ~19 % of a core (~74 % total) → load ~5.2 on 4 cores.

**Mitigations:**
1. **Fit the official Raspberry Pi 5 Active Cooler** (~€5–10 clip-on heatsink+fan). It keeps the SoC
   ~50–60 °C under load and removes the throttling. *This is the real fix (cooler on order 2026-07-06).*
2. Meanwhile, run the **light bring-up** (`use_camera:=false use_docking:=false`) — kills those three
   processes (~74 % of a core freed), drops load well under 4, and lets the Pi cool. This is the right
   default on the current (guest) Wi-Fi anyway (no camera flood).

Monitor: `watch -n1 "vcgencmd measure_temp; vcgencmd get_throttled"`.
[`get_throttled` bit reference](https://www.raspberrypi.com/documentation/computers/os.html#get_throttled).

## Good to know / gotchas
- **8 GB of RAM** (6.4 GB free under the stack) — RAM is not the constraint; the **thermal cap above** is
  what limits sustained compute. Heavy builds (Nav2, micro-ROS) still build faster sequentially.
- Watch **temperature** (`vcgencmd measure_temp`) and **throttling / under-voltage**
  (`vcgencmd get_throttled` — see "Thermal" above; a `brownout` at bring-up is a *power* issue, see
  [power.md](../power_distribution/power.md)).
- Always use `/dev/serial/by-id/...` paths (`ttyACM0`/`ttyUSB0` numbers can change on reboot).
