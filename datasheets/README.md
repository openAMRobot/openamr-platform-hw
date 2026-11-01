# Datasheets

Manufacturer datasheets and manuals for the components used on (or offered as options for) the
OpenAMRobot base. Also here: the **[motor / gearbox / driver sizing calculations](motor-sizing-calculations.md)**
for the wheel–motor–driver mechatronic chain.

> ⚠️ **Third-party documents — copyright of their respective manufacturers.** These PDFs are
> **re-hosted for convenience** with attribution to the source (see each folder). They are **not**
> covered by this repository's licence; all rights remain with the manufacturers. If you redistribute,
> keep the attribution, or download the current versions from the manufacturers directly.

## What applies to the base build vs. what is optional

The existing robot (v0.0.1) documented in this repo uses the **ZD** motor + driver. The **ZLTECH ZLLG80ASM250-L-B** and **ZLAC8015D V4.2** are the selected 2.0 drivetrain. The TZBOT battery and BMS are **optional**; they are **not** the 2.0 battery. The TZBOT WCM-500-24 wireless charger is the 2.0 and release 001 charging path.

| Folder | Component | On the base build? |
|---|---|---|
| [`ZDmotor/`](ZDmotor/) | ZD BLDC motor (Z4BLD60-24GN-30S) + **ZBLD.C20-120L2R** driver | existing robot (v0.0.1), legacy |
| [`ZLTech/drivers/`](ZLTech/drivers/) | ZLAC8015D V4.2 driver (CANopen on CAN1; RS485 not used in 2.0); ZLAC8030L reference only | yes, the 2.0 drivetrain |
| [`ZLTech/wheel_ZLLG80ASM250/`](ZLTech/wheel_ZLLG80ASM250/) | ZLLG80ASM250-L-B hub motor | yes, the 2.0 drivetrain |
| [`TZBot/battery_BMS/`](TZBot/battery_BMS/) | 24 V 20 Ah battery + BMS (serial protocol) | ⚙️ option (product battery/BMS) |
| [`TZBot/charger/`](TZBot/charger/) | TZBOT WCM-500-24 wireless charger (2.0 and release 001 charging path) | Yes, the 2.0 design (register CHARGING) |

See [product-architecture.md](../product-architecture.md) for how the base and the options fit
together.

## OpenAMRobot 2.0 controller and sensor references

| Folder | References |
|---|---|
| [`STMicroelectronics/STM32H723ZG/`](STMicroelectronics/STM32H723ZG/) | STM32H723ZG datasheet DS13313, NUCLEO-H723ZG UM2407 and MB1364 schematic; ES0491 errata. RM0468 metadata and source are recorded in the folder readme. |
| [`MaxBotix/MB7060/`](MaxBotix/MB7060/) | XL-MaxSonar-WR/WRC datasheet, document code 11838ab. |
| [`Benewake/TF-Luna/`](Benewake/TF-Luna/) | TF-Luna datasheet and user manual, retained in separate subfolders under their vendor filename en.pdf. |
| [`TDK/ICM-42688-P/`](TDK/ICM-42688-P/) | ICM-42688-P datasheet DS-000347. |
| [`MikroE/6DOF_IMU_14_Click/`](MikroE/6DOF_IMU_14_Click/) | 6DOF IMU 14 Click schematic; reference only, the 2.0 IMU board is the TDK EV_ICM-42688-P (BOM Issue 7.14). |
| [`TI/ISO1212/`](TI/ISO1212/), [`TI/TPL7407L/`](TI/TPL7407L/) | Link-only metadata; TI terms prohibit other reproduction and display of these PDFs. |

The RM0468 reference manual (about 66 MB) is not stored in this repository because of its size.
Download it from ST; the source link, revision and SHA-256 are in
[`STMicroelectronics/STM32H723ZG/readme.md`](STMicroelectronics/STM32H723ZG/readme.md).
