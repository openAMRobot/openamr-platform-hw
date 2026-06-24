# Safety

*Last updated: 2026-06-17.*

## Motor / movement tests
1. **Wheels off the ground** for all initial motor tests.
2. **24 V on** only when you need the wheels to turn; keep a **hand on the 24 V cut-off**.
3. **Low speeds** to start (the guide recommends max 0.05 m/s linear, 0.15 rad/s angular).
4. The firmware has a **200 ms command watchdog**: no `/cmd_vel` → motors stop. Don't rely on it alone.
5. Stop ways: `k` (teleop), `Ctrl-C` (publisher), or the 24 V cut-off.
6. A **ROS-independent physical E-stop** is recommended (not confirmed present yet — see [../hardware/power.md](../../electrical/power_distribution/power.md)).

## ⚠️ Electrical — 230 V AC
The AC/DC converter is fed by **230 V mains, which is potentially lethal.** If its terminals are exposed:
- **30 mA RCD** upstream (top priority life-saver),
- **enclose** all mains wiring, **earth** the chassis, **fuse** the input,
- **cut/unplug mains before touching** the power side — never work live.

Full details: [../hardware/power.md](../../electrical/power_distribution/power.md).

## Software / firmware changes
- Don't flash a new firmware without knowing you can re-flash a working one (the Teensy can't be dumped;
  source is in `~/linorobot2_hardware`).
- After any firmware/config change, **re-verify** encoder directions and a low-speed `/cmd_vel` before
  driving normally.

## Equipment
- ⚠️ Do **not** kill the LiDAR driver brutally mid-scan (it gets stuck → unplug/replug). See
  [../hardware/lidar.md](../../electrical/sensors/lidar.md).
- Common ground: drivers' `COM` ↔ Teensy GND, always.

## Before autonomy (Nav2 / docking)
Do not enable SLAM/Nav2/docking until manual motion, encoder direction, odometry, and stopping behaviour
are all validated (per the bring-up guide's gates).
