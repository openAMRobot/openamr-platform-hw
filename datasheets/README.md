# Datasheets

Manufacturer datasheets and manuals for the components used on (or offered as options for) the
OpenAMRobot base. Also here: the **[motor / gearbox / driver sizing calculations](motor-sizing-calculations.md)**
for the wheel–motor–driver mechatronic chain.

> ⚠️ **Third-party documents — copyright of their respective manufacturers.** These PDFs are
> **re-hosted for convenience** with attribution to the source (see each folder). They are **not**
> covered by this repository's licence; all rights remain with the manufacturers. If you redistribute,
> keep the attribution, or download the current versions from the manufacturers directly.

## What applies to the base build vs. what is optional

The base OpenAMRobot documented in this repo uses the **ZD** motor + driver. The **ZLTech** and
**TZBot** parts are **alternative / optional** components for larger product configurations
(higher-power drives, wireless charging, lift, larger battery) — they are **not** on the base build.

| Folder | Component | On the base build? |
|---|---|---|
| [`ZDmotor/`](ZDmotor/) | ZD BLDC motor (Z4BLD60-24GN-30S) + **ZBLD.C20-120L2R** driver | ✅ **yes — this is the base** |
| [`ZLTech/drivers/`](ZLTech/) | ZLAC8015D / ZLAC8030L industrial drivers (CANopen/RS485) | ⚙️ option (higher-power variant) |
| [`ZLTech/wheel_ZLLG80ASM250/`](ZLTech/wheel_ZLLG80ASM250/) | ZLLG80 hub-motor wheel | ⚙️ option (alternative drivetrain) |
| [`TZBot/battery_BMS/`](TZBot/battery_BMS/) | 24 V 20 Ah battery + BMS (serial protocol) | ⚙️ option (product battery/BMS) |
| [`TZBot/charger/`](TZBot/charger/) | WCM-300 wireless charger | ⚙️ option (auto-docking charge) |
| [`TZBot/lift/`](TZBot/lift/) | Lift reducer (TZDSXZ-48-400) | ⚙️ option (lift attachment) |

See [product-architecture.md](../product-architecture.md) for how the base and the options fit
together.
