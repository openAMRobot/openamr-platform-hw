# Bill of Materials (BOM) repository

## Overview

This document provides a comprehensive list of all assemblies and their corresponding files in the BOM repository. It also includes details on sheet metal parts, fasteners, technological operations, and origin components.

## Sheet metal parts

Sheet metal parts are subject to production variations. The current designs are based on the following coefficients and radii:

- **Coefficient (K):** 0.47
- **Sheet metal specifications:**
  - **0.8 mm Sheet:** Radius (R) = 1.2
  - **1.2 mm Sheet:** Radius (R) = 1.5
  - **2.0 mm Sheet:** Radius (R) = 2.4

### Post-production

- Parts may be painted after bending.
- Riveting nuts can be installed before painting if the threaded part is protected from the coating.
- Screws installed without lock washers should be secured with a thread lock (e.g., Loxeal 55-03).

**Note:** All components are highly interconnected and their functionality is dependent on one another.

## MMP - Multipurpose Mobile Platforms

### List of fasteners and quantities

Detailed information on fasteners and their quantities used in assemblies is listed in the corresponding sections.

### Technological operations

Each assembly comes with a list of required technological operations. Ensure that all operations are followed as specified.

## Origin components

The following components are used in the assemblies:

- **Heavy duty drive wheel:** Blickle GEVN 200/30H7
- **Light duty swivel castor:** Blickle LPA-VSTH 35K
- **Oval flange bearing units:**
  - REXNORD UCFL 205 C 655472 (d25)
  - REXNORD UCFL 206 C 666412 (d30)
- **Rivet nuts:**
  - M4 Blind Rivet Nut - Round Thin - Stainless Steel
  - M5 Blind Rivet Nut - Round Thin - Stainless Steel
  - M6 Blind Rivet Nut - Round Thin - Stainless Steel
  - M8 Blind Rivet Nut - Round Thin - Stainless Steel
- **Feather keys:**
  - 4x4x25 DIN 6885-UNI 6604 (formerly ISO 773)
  - 8x7x28 DIN 6885-UNI 6604 (formerly ISO 773)
- **Screwed spacer sleeve:** TFF-M3/25 FIX&FASTEN
- **BLDC Motor:** Z4BLD60-24GN-30S/4GN 25K 
- **Laser range scanner:** RPLIDAR S3 (S3M1-R2), 2.0 navigation LiDAR, 4 × M2.5 (screw engagement ≤ 4 mm). Legacy (existing robot): RPLIDAR A1-A1M8
- **LiDAR mount spacer:** MMP.07.00.00.002, **17.5 mm** thick, 3D printed (see below), directly on the MMP.07 bracket without standoffs; S3 beam 174.0 + 17.5 + 30.55 = 222.05 mm above the floor. Was a 7.1 mm spacer plate on the 10 mm standoffs of the A1 bracket (BOM Issue 7.7 MEC-008)
- **Camera module:** NVision Assem
- **Proximity sensor:** E18-D80NK
- **US sensor:** JSN-SR04T
- **LED module:** 3 LED RGB Module 0.72W SWP

## 3D-printed parts

FDM print in PETG, at least 4 perimeters and 40 % infill. STEP and STL are in
`mechanical/cad/production_files`.

| Part number | Name | Qty | Size (mm) | Notes |
|---|---|---|---|---|
| MMP.01.00.00.003 | Camera mount | 1 | 144 x 42 x 32 | Orbbec Gemini 336L, 10° up face |
| MMP.00.00.00.005 | TF-Luna mount | 2 | 52 x 9 x 23 | Front and back panel centre; 10° sensor face |
| MMP.00.00.00.006 | Ultrasonic mount | 4 | 55 x 40 x 32 | MB7060, front and back panel edges, y ±130 mm |
| MMP.07.00.00.002 | LiDAR mount spacer | 1 | 80 x 70 x **17.5** | Under the RPLIDAR S3, no standoffs |
| MMP.02.00.00.002 | Motor driver mount | 1 | 170 x 30 x 28 | ZLAC8015D to the base plate |

Sheet metal and plate parts for the electronics (STEP only, no DXF yet):

| Part number | Name | Qty | Notes |
|---|---|---|---|
| MMP.04.00.00.002 | Electronics bracket | 1 | 2 mm sheet, under and in front of the center bracket; Jetson and IMU |
| MMP.04.00.00.003 | STM32 Click mount plate | 1 | 6 mm plate, 100 x 90 mm; STM32 and Click boards, on anti-vibration standoffs |

__________________________________________________________

# OpenAMRobot – Preliminary Electronics Bill of Materials (BOM)

## Overview

This Bill of Materials preliminary defines the electronics used in the OpenAMRobot development platform.  
The system follows a two-layer architecture:

- **High-level control**: Raspberry Pi 5 (ROS2, navigation, perception, UI)  
- **Real-time control**: Teensy 4.0 (motor control, encoders, IMU)  

The setup is designed for differential drive mobile robot development and software validation.

---

## Core Computing

| Item | Model | Qty | Description |
|------|------|-----|------------|
| Main Computer | Raspberry Pi 5 (8GB) | 1 | High-level controller running ROS2, SLAM, navigation, and UI |
| Microcontroller | Teensy 4.0 | 1 | Real-time controller for motors, sensors, and low-level logic |
| Communication | USB cable (USB-A ↔ Micro USB / USB-C) | 1 | Serial communication between Raspberry Pi and Teensy |

---

## Drive System

| Item | Model | Qty | Description |
|------|------|-----|------------|
| BLDC Motor | ZDBLD60-24GN-30S | 2 | 24V BLDC motor for differential drive |
| Gearbox | 4GN 25K | 2 | Gear reduction for torque increase |
| Motor Driver | ZBLD-C20-120L2R | 2 | BLDC motor driver (PWM speed control, digital direction control) |

---

## Feedback Sensors

| Item | Model | Qty | Description |
|------|------|-----|------------|
| Magnetic Encoder | AS5040 | 2 | Wheel position sensing for odometry (Quadrature (A/B) or SPI interface) |
| IMU | MPU6500 | 1 | 6-axis inertial measurement unit (accelerometer + gyroscope, I2C). Gate A unit (legacy), superseded by BOM Issue 7.7: 2.0 IMU is the ICM-42688-P |

---

## Perception Sensors

| Item | Model | Qty | Description |
|------|------|-----|------------|
| LiDAR | RPLIDAR S3 (S3M1-R2) | 1 | 2.0 navigation 2D laser scanner for SLAM and obstacle detection (USB via USB to UART adapter; regulated 5 V rail). Replaces the RPLIDAR A1 — legacy (existing robot) |
| Camera | Raspberry Pi Camera Module / Arducam IMX219 | 1 | Vision sensor for docking and computer vision tasks (CSI interface). Gate A unit, superseded by BOM Issue 7.7 |

---

## Power System

| Item | Model | Qty | Description |
|------|------|-----|------------|
| Battery | 24V Li-ion / LiFePO4 pack | 1 | Main power source for motors and electronics |
| DC-DC Converter | LM2596 Buck Converter (24V → 5V, ≥5A) | 1 | Power supply for Raspberry Pi |
| DC-DC Converter | DROK 24V → 5V/12V Step-Down Module, legacy (Gate A unit), superseded by BOM Issue 7.7 | 1 | Power supply for sensors and auxiliary electronics on the existing robot. OpenAMRobot 2.0 has no 12 V rail |
| Protection | Inline fuse (rated above motor current) | 1 | Overcurrent protection on main power line |
| Safety | Emergency stop switch | 1 | Manual power cutoff for safety |

---

## Interfaces and Integration

| Item | Model | Qty | Description |
|------|------|-----|------------|
| Prototyping Board | Breadboard / Perfboard | 1 | Temporary wiring platform (used until custom PCB is developed) |
| Power Distribution | Terminal blocks / distribution bus | 1 set | Power routing for 24V and low-voltage lines |
| Wiring | Motor cables, signal wires, connectors | 1 set | Electrical connections between components |

---

## Alternative Drive Option (ZL Tech)

| Item | Model | Qty | Description |
|------|------|-----|------------|
| Hub Motor | ZLLG80ASM250-L-B | 2 | Integrated BLDC motor with built-in encoder (BOM Issue 7.7 selection; exact order code under confirmation in PR #17) |
| Driver | ZLAC8015D | 1–2 | Motor controller with RS485/CAN interface. Gate A unit, superseded by BOM Issue 7.7 |

---

## System Interfaces Summary

- Raspberry Pi ↔ Teensy: USB Serial  
- Teensy ↔ Motor Drivers: PWM (speed) + Digital IO (direction)  
- Teensy ↔ Encoders: Quadrature (A/B) or SPI interface  
- Teensy ↔ IMU: I2C  
- Raspberry Pi ↔ LiDAR: USB (RPLIDAR A1, legacy (existing robot)); 2.0: Jetson ↔ RPLIDAR S3 via USB to UART adapter  
- Raspberry Pi ↔ Camera: CSI  

---

## Notes

- The system is designed for modular expansion and hardware replacement.  
- Breadboard or perfboard is used for initial prototyping before designing a custom carrier PCB.  
- All components are selected to support ROS2-based mobile robotics development.  

[![Donate via PayPal](https://img.shields.io/badge/Donate-PayPal-blue.svg)](https://www.paypal.com/paypalme/BotshareAI)
[![Donate on GitHub](https://img.shields.io/badge/Sponsor%20on-GitHub-pink?logo=github-sponsors)](https://github.com/sponsors/openAMRobot)
