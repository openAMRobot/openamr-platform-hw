# Raspberry Pi 5 — main computer

*Last updated: 2026-06-17.*

## Role
The high-level "brain". Runs **ROS 2**, the micro-ROS agent (bridge to the Teensy), the USB/CSI
sensor drivers (LiDAR, camera), odometry, and later the navigation (Nav2/SLAM).

## Specifications
| | |
|---|---|
| Model | Raspberry Pi 5 Model B Rev 1.1 |
| CPU | 4× ARM Cortex-A76, **aarch64 / ARM64** |
| RAM | ~4 GB |
| OS | Ubuntu Server **24.04 LTS** (Noble) |
| Kernel | 6.8.x-raspi |
| ROS | **ROS 2 Jazzy** (`/opt/ros/jazzy`) |
| Hostname | `BOTSHARE` |
| User | `botshare` (groups: `dialout`, `video`, `sudo`, …) |

## Communication
- **To the Teensy**: USB → `/dev/ttyACM0` (stable: `/dev/serial/by-id/usb-Teensyduino_USB_Serial_16778200-if00`).
  The Pi hosts the **micro-ROS agent** that exposes the Teensy's topics. See 01-communication.md (see `openamr-platform-sw`: communication doc).
- **To the LiDAR**: USB → `/dev/ttyUSB0` (CP2102 UART bridge).
- **To the camera**: **CSI** (ribbon cable), not USB.
- **ROS internal**: DDS = **CycloneDDS** (rmw_cyclonedds_cpp, adopted 2026-06-18 for Nav2/docking).

## Important directories (`/home/botshare`)
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

## Good to know / gotchas
- **4 GB of RAM**: heavy builds (Nav2, micro-ROS) → build sequentially; it takes a while.
- Watch **temperature / under-voltage** (`vcgencmd measure_temp`, `vcgencmd get_throttled`).
- Always use `/dev/serial/by-id/...` paths (`ttyACM0`/`ttyUSB0` numbers can change on reboot).
