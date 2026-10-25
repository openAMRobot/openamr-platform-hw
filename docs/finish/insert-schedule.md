# Insert and trim schedule, mobile base

An insert or trim is any part added only for appearance. The plan keeps them few, light and removable,
with no new holes and no adhesive on functional surfaces.

## Inserts on the mobile base

**None.** The mobile base carries no accent colour and no added trim. Its appearance comes from the
panel and cover colours (RAL 7035 and RAL 7016) and the black printed mounts, all listed in the
[finish schedule](finish-schedule.md).

## Inserts on the whole robot (for reference)

The robot's only inserts are on the upper body and are scheduled in
[openamr-upperbody-hw `docs/finish/insert-schedule.md`](https://github.com/openAMRobot/openamr-upperbody-hw/blob/main/docs/finish/insert-schedule.md).
They are listed here so that the base team can check clearances to the base.

| Ref | Insert | Location | Colour | Status |
|---|---|---|---|---|
| I1 | Slot cover strip, left face of the arm profile | front-most slot, from the adapter plate up to the left J1_A plate | RAL 5018 cyan | verify |
| I2 | Slot cover strip, right face of the arm profile | front-most slot, from the adapter plate up to the right J1_A plate | RAL 5018 cyan | verify |
| I3 | OpenArm printed inserts | parts to be identified from the Enactic 2.0 BOM or CAD | RAL 2004 orange | verify |

None of them is on or next to the mobile base: the lowest insert (I1, I2) starts at the adapter plate,
844 mm above the floor at lift 0, about 630 mm above the top edge of the front panel (215 mm in the
model), which carries the base E-stop.

## Keep-out rule K1 (safety colours)

| Device | Where | Colour kept | Keep-out |
|---|---|---|---|
| S1 base E-stop, XB4BS8445 with ZBE-102 (BOM row SAF-001) | front panel | red mushroom on yellow legend | no orange or cyan within 150 mm of the bezel edge; no accent on the front panel |
| RESET button, XB4BW36B5 (BOM row SAF-005) | verify (not in the v0.2 CAD) | standard blue | no orange or cyan within 150 mm of the bezel edge; no accent on its panel |
| S2 chest E-stop (OpenArm kit button) | upper body, verify | red on yellow | as above; applies to I1, I2, I3 |

The 150 mm distance is a proposal of this plan, not a standard value; the safety owner may set another.

## Trims considered and not used

| Trim | Reason |
|---|---|
| Rubber edge protectors on panel or cover edges | excluded by the brief; edges are deburred and broken 0.1 to 0.3 mm per the drawings |
| Bumper strips | excluded by the brief; no bumper function is claimed |
| Stripes or large accent areas on panels or cover | excluded by the design direction |
| Film or vinyl on the steel panels | unnecessary on powder-coated steel; adhesive on functional surfaces is not allowed |
| Coloured rings or bezels around sensors | would sit at sensor apertures; apertures stay unchanged |
| Branding parts (BOM row MEC-017) | geometry and material are not defined; no colour is proposed until the cover drawing defines them |

## Fit checks for the base

None; no insert is fitted to the base. The masking checks for the base are in
[masking-and-assembly.md](masking-and-assembly.md).
