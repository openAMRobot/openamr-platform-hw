# Mass properties of the OpenAMRobot 2.0 mobile base from CAD

Computed on 14 Nov 2026 by [the CAD mass properties tool](../../tools/cad_massprops/README.md) from the STEP files on
main (8ed2b06). Compared with the roadmap model mass ledger of openamrobot-docs main (852c32c, snapshot 9 Nov 2026,
robot 87.109 kg). Nothing was weighed. Every material and mass has a source in
[`materials.yaml`](../../tools/cad_massprops/materials.yaml); estimates are marked.

Data: [`part_massprops.csv`](part_massprops.csv) (one row per file),
[`link_comparison.csv`](link_comparison.csv) (part, BOM line and URDF link comparison) and
[`massprops.json`](massprops.json) (the same numbers and the assembly roll-up).

## Summary

- The sheet-metal chassis MEC-001 (13 parts, steel EN 1.0114 per the drawings) weighs **18.549 kg** from the STEP
  volumes. The ledger has **15.766 kg**. The difference is **+2.783 kg (+17.7 %)**.
- Cause: the ledger takes the volume of the roadmap model meshes (base_glb.js) times 7850 kg/m3. Those meshes hold
  2 % to 21 % less volume than the STEP solids. The density is the same (7850 kg/m3). The material assumption of the
  ledger (steel) is now confirmed by the drawings.
- base_link with the CAD values substituted: **52.692 kg** instead of 49.948 kg (+2.744 kg, +5.5 %). Its inertia rises by
  17 % to 24 % on the three axes. Its centre of mass moves 3 mm down.
- Hub motors: the in-repository datasheet gives **3.60 kg** each (V1.0 double-shaft drawing). The ledger has 3.45 kg.
  The selected B2 V1.01 drawing has no weight. +0.150 kg per motor (+4.3 %).
- Robot total with these changes: about **90.15 kg** instead of 87.109 kg. This excludes three parts on base_link that
  have no documented material and no ledger line (291.4 cm3 together; see below).
- The front panel unit problem does not reproduce. `MMP.00.00.00.001 Front panel.STEP` declares millimetres and reads
  384.8 x 165.0 x 20.0 mm, which matches its drawing. The 385 m box comes from the reader setup (see
  [Front panel length unit](#front-panel-length-unit)). The file needs no re-export for its unit.
- The full assembly STEP places the base sheet 8.8 mm too low and 12.6 mm to the side. The roll-up corrects this. The full
  assembly needs a re-export (see [Files that need re-export or a document fix](#files-that-need-re-export-or-a-document-fix)).

## Ranked differences

Differences above 5 % or above 50 g, largest absolute difference first. Part rows compare one piece. The ledger value of
a MEC-001 part is its roadmap mesh volume x 7850 kg/m3 (the method of `analyse.py`); these 13 values sum to the ledger
15.766 kg exactly.

| Rank | Item | Ledger kg | CAD kg | Difference kg | Difference % | Basis of the CAD value |
|---|---|---|---|---|---|---|
| 1 | MEC-001 chassis, deck and panels (13 parts) | 15.766 | 18.549 | +2.783 | +17.7 | STEP volume x 7850 (drawings: steel EN 1.0114) |
| 2 | MMP.02.00.00.001 Base | 5.736 | 6.966 | +1.229 | +21.4 | STEP volume x 7850 |
| 3 | MMP.04.00.00.001 Center bracket | 2.488 | 3.102 | +0.615 | +24.7 | STEP volume x 7850 |
| 4 | MMP.01.00.00.001 Cover | 1.983 | 2.407 | +0.424 | +21.4 | STEP volume x 7850 |
| 5 | MMP.07.00.00.001 Lidar support (MEC-008) | 0.577 | 0.300 | -0.277 | -48.0 | STEP volume x 7850 (drawing: 1.2 mm steel EN 1.0114); ledger value was an estimate |
| 6 | MMP.00.00.00.002 Back panel | 1.021 | 1.231 | +0.209 | +20.5 | STEP volume x 7850 |
| 7 | DRV-001 hub motor (each, 2 pieces) | 3.450 | 3.600 | +0.150 | +4.3 | datasheet, not CAD (above 50 g) |
| 8 | MMP.01.00.00.002 Cover flange (each, 2 pieces) | 0.346 | 0.400 | +0.054 | +15.7 | STEP volume x 7850 |
| 9 | MMP.00.00.00.006 Ultrasonic mount (each, 4 pieces) | 0.015 | 0.066 | +0.051 | +343 | STEP volume x 1270, PETG at 100 % infill (estimate, upper bound) |
| 10 | MMP.01.00.00.003 Camera mount (MEC-009) | 0.040 | 0.074 | +0.034 | +84 | STEP volume x 1270, PETG at 100 % infill (estimate, upper bound) |
| 11 | MMP.05.00.00.001 Support (each, front left and rear right) | 0.126 | 0.159 | +0.033 | +26.3 | STEP volume x 7850 |
| 12 | MMP.05.00.00.001-01 Support, mirrored (each, front right and rear left) | 0.139 | 0.159 | +0.021 | +14.9 | STEP volume x 7850 |

Within the limits: front panel +0.046 kg (+4.2 %), side panels +0.022 kg each (+2.0 %), TF-Luna mounts 0.010 kg each
(+0.3 %).

Not compared, material unknown (no CAD mass). Three of them are not in the ledger at all:

| Part | Volume cm3 | In the ledger |
|---|---|---|
| MMP.04.00.00.002 Electronics bracket | 189.84 | no |
| MMP.07.00.00.002 Lidar mount spacer (MEC-008) | 97.10 | yes, 0.023 kg estimate |
| MMP.02.00.00.002 Motor driver mount | 57.07 | no |
| MMP.04.00.00.003 STM32 Click mount plate | 44.53 | no |

The electronics bracket has the largest volume of the four, about half the volume of the centre bracket. Its material
matters for base_link.

## URDF link comparison

| Link | Ledger kg | CAD kg | Difference | Ledger COM in the link frame (m) | CAD COM (m) | Ledger inertia diagonal (kg m2) | CAD inertia diagonal (kg m2) |
|---|---|---|---|---|---|---|---|
| base_link | 49.948 | 52.692 | +2.744 kg, +5.5 % | (-0.0664, -0.0047, 0.0701) | (-0.0648, -0.0045, 0.0671) | 1.5516, 2.2075, 3.1228 | 1.8243, 2.7379, 3.6521 |
| left_wheel_link | 3.450 | 3.600 | +0.150 kg, +4.3 % | (0, 0, 0) | not derived | 0.0196, 0.0230, 0.0196 | 0.0092, 0.0149, 0.0092 (estimate) |
| right_wheel_link | 3.450 | 3.600 | +0.150 kg, +4.3 % | (0, 0, 0) | not derived | 0.0196, 0.0230, 0.0196 | 0.0092, 0.0149, 0.0092 (estimate) |

base_link, how the CAD value is built: the ledger link minus its MEC-001, MEC-008 support, MEC-009, MEC-010 and MEC-011
items, plus the same parts from the CAD (mass, centre and full tensor from the placed STEP solids; camera mount at its
ledger position because its full assembly body is empty). The rest of the link keeps the ledger masses, positions and
box inertias, so the result has small products of inertia from the CAD parts only:

```text
base_link (CAD substituted), about its centre of mass, base_link axes, kg m2
ixx 1.824279  ixy -0.000239  ixz  0.002903
              iyy  2.737881  iyz  0.000714
                             izz  3.652115
```

Wheel links: the mass is the datasheet value. The inertia is the B2 V1.01 STEP at uniform density (2502 kg/m3) scaled to
3.60 kg. A motor has its copper and steel near the axle and rubber outside, so this is an estimate only. The uniform
centroid lies 4.3 mm from the tyre mid-plane toward the brake side. The ledger keeps the whole motor on the spinning
wheel link (audit conflict M4); this report does not change that.

Castor, castor wheel and lidar links carry purchased parts only. They are not compared.

## Assembly roll-up and the base_link transform

### Frame of the full assembly STEP

`mechanical/cad/Full_assembly_STEP/MMP.00.00.00.000_full_assembly.STEP.zip` (Autodesk export of 15 Oct 2026, version
v26) gives the placement of every part. Its frame, found from the geometry:

- X forward: the front panel is at X +370 to +390 mm, the back panel at -390 to -370 mm.
- Y up: the floor is Y = 0. The 200 mm wheels of the legacy drive reach Y = -2 mm, the model's 2 mm tyre compression.
- Z to the right (right-handed). The STM32 Click mount plate, an asymmetric part, is at Z -36 to +64 mm. The
  roadmap model has it at y -64 to +36 mm.
- The legacy wheel axle is at X = 0, Y = 98 mm, wheel centres at Z = +/-199.75 mm. This is where the model puts the
  2.0 axle and base_link (base_link 0.098 m above base_footprint, P-03 item 8, facts.yaml base_link_z).

So the full assembly origin is base_footprint, with axes turned. The transform is:

```text
p_base_footprint = R p_cad              R = [[1, 0, 0], [0, 0, -1], [0, 1, 0]]   (x = X, y = -Z, z = Y)
p_base_link      = R p_cad - (0, 0, 0.098 m)
I_base_link      = R I_cad R^T
URDF: the CAD assembly frame in base_link is  <origin xyz="0 0 -0.098" rpy="1.5707963 0 0"/>
```

Check: with this transform the centres of 23 placed parts lie 0.0 mm to 7.2 mm from the centres of the roadmap model
meshes. The cover (13.7 mm) is the exception; its roadmap mesh holds 18 % less volume.

Limit: the 2.0 hub motors are not in the CAD yet (the full assembly still has the legacy MMP.03 drive). The transform
assumes the 2.0 axle stays at the legacy axle, as the model does. If M-02 moves the axle, base_link moves with it.

### Placement correction

The full assembly places `MMP.02.00.00.001 Base` at (+1.49, +43.22, -12.57) mm. Its deck bottom is then at 43.2 mm and
its sides at -302.6 and +277.4 mm. `MMP.02.00.00.000 Base assembly.STEP`, the 52 mm deck underside datum (BOM
Mechanical sheet) and the parts standing on the deck (centre bracket, supports, lidar support, driver mount, all at
Y = 54 mm) put it at (0, 52, 0) mm. The roll-up uses (0, 52, 0) mm. The original box is kept in `massprops.json`.

### Results

MEC-001 sheet-metal chassis: 13 placed parts (base, front and back panel, 2 side panels, cover, 2 cover flanges, centre
bracket, 4 supports).

| Frame | Mass kg | Centre of mass (m) | Inertia about the centre of mass (kg m2) |
|---|---|---|---|
| CAD assembly | 18.548 | (-0.00134, 0.14397, 0.00000) | ixx 0.744072, iyy 1.750997, izz 1.342119, ixy -0.000935, ixz 0.000012, iyz -0.000001 |
| base_footprint | 18.548 | (-0.00134, 0.00000, 0.14397) | ixx 0.744072, iyy 1.342119, izz 1.750997, ixy -0.000012, ixz -0.000935, iyz 0.000001 |
| base_link | 18.548 | (-0.00134, 0.00000, 0.04597) | as base_footprint |

The ledger models MEC-001 as one solid box of 0.78 x 0.582 x 0.165 m at (0, 0, 0.150) m in base_footprint. Its box
inertia is ixx 0.481, iyy 0.835, izz 1.244 kg m2. The sheet-metal shell has 55 %, 61 % and 41 % more, because its mass
sits on the outside. Its centre is 6 mm lower.

All placed parts with a known material (MEC-001 plus lidar support, 2 TF-Luna mounts and 4 ultrasonic mounts, 20
instances): 19.133 kg, centre (0.00351, -0.00002, 0.04496) m in base_link, inertia ixx 0.751222, iyy 1.411600,
izz 1.824768, ixy 0.000121, ixz 0.000079, iyz 0.000013 kg m2. The camera mount is not in it (its body is empty in the
full assembly); the four parts of unknown material are not in it.

## Front panel length unit

`MMP.00.00.00.001 Front panel.STEP` declares `SI_UNIT(.MILLI.,.METRE.)` for its geometry. A second unit,
`SI_UNIT($,.METRE.)`, is only used by the density property. With the reader set up correctly it reads 384.8 x 165.0 x
20.0 mm, the drawing size (385 x 165 x 20 mm).

The 385 m box appears when `Interface_Static.SetCVal_s("xstep.cascade.unit", "M")` is called before the STEP controller
exists. That first call returns False and changes nothing. The first `STEPControl_Reader` then initialises the
controller, and the first file is read in millimetres. From the second file on, the setting works. The front panel is
the first file in alphabetical order, so only it looked wrong. Reproduced here: front panel 384.84 (unscaled), back panel
0.3848 m, front panel again 0.3848 m. The tool calls `STEPControl_Controller.Init_s()` first and checks the result. It
also compares every box with its drawing and would correct and report a scale factor of 1000, 0.001 or 25.4. No file
needed it.

## Files that need re-export or a document fix

Re-export:

1. `mechanical/cad/Full_assembly_STEP/MMP.00.00.00.000_full_assembly.STEP.zip`: base sheet off its design position
   (above); the camera mount body `camera_mount v8` is empty (no geometry, only the camera inside); still the legacy MMP.03
   wheel assemblies (Z4BLD60 gear motor, 200 mm wheel, flange bearings, drive shaft) and the earlier single 8S1P battery
   package, not the 2.0 hub motors, shaft-flat brackets and two battery trays. Re-export after the M-02 drivetrain is in
   the CAD.
2. Part files exported from Autodesk with the default material property "Celik" (steel) 7850 kg/m3:
   `MMP.00.00.00.001 Front panel`, `MMP.00.00.00.002 Back panel`, `MMP.00.00.00.005 TF-Luna mount`,
   `MMP.00.00.00.006 Ultrasonic mount`, `MMP.01.00.00.003 Camera mount`, `MMP.02.00.00.002 Motor driver mount`,
   `MMP.04.00.00.002 Electronics bracket`, `MMP.04.00.00.003 STM32 Click mount plate`,
   `MMP.07.00.00.002 Lidar mount spacer`. For the panels it agrees with the drawing. For the printed PETG mounts it is
   wrong. A CAD tool that reads the STEP material will compute steel masses for them. Re-export with the real material or
   without one.
3. No file needs re-export for its length unit.

Document fixes (no STEP change):

4. No material on any document for `MMP.04.00.00.002 Electronics bracket`, `MMP.02.00.00.002 Motor driver mount`,
   `MMP.04.00.00.003 STM32 Click mount plate` and `MMP.07.00.00.002 Lidar mount spacer`. The first three have no BOM line
   and are missing from the mass ledger.
5. MEC-008 conflict: the BOM line title says "LiDAR spacer plate, aluminium", the line text and M-01 say "17.5 mm printed
   spacer MMP.07.00.00.002".
6. `MMP.03.00.00.002 Wheel bracket inner.PDF` has no material in its title block (legacy part).
7. The Weight field is empty on every drawing. No drawing mass exists to check against.
8. The hub motor B2 V1.01 drawing leaves the weight empty. The ledger cites a "V1.0 specification" of 3.45 kg that is not
   in this repository; the V1.0 drawing that is here says 3.60 kg +/- 5 %. Ask the manufacturer for the B2 weight or weigh
   one motor.

For the roadmap model (openamrobot-docs, not changed here): the chassis meshes in `base_glb.js` hold 2 % to 21 % less
volume than the STEP. The ultrasonic mount mesh (41.4 cm3 against 52.3 cm3) and the STM32 plate mesh (21.8 cm3 against
44.5 cm3) look like other revisions. Taking MEC-001 from the STEP volumes, or regenerating the meshes from the STEP, closes
the 2.8 kg gap.

## Materials

| Material | Density kg/m3 | Density source | Parts |
|---|---|---|---|
| Steel EN 1.0114 (S235JR) | 7850 | EN 1993-1-1 clause 3.2.6 | the 13 MEC-001 parts, lidar support; legacy outer wheel bracket and motor bracket. Each from its drawing title block. |
| Steel 37Cr4 | 7850 | nominal steel value, no alloy value in the repository (estimate) | legacy drive shaft, from its drawing |
| PETG | 1270 | PETG resin density 1.27 g/cm3 (ISO 1183 datasheet value), as in the roadmap model (estimate) | TF-Luna mount (BOM MEC-010), ultrasonic mount (MEC-011), camera mount (MEC-009) |
| unknown | none | no document names it | electronics bracket, motor driver mount, STM32 Click mount plate, lidar mount spacer, plastic cover, legacy inner wheel bracket, PT1 parts |

Printed parts are computed at 100 % infill. With the usual infill they weigh less. The infill is not documented.

Purchased parts use the datasheet or BOM mass, not the CAD volume: hub motor 3.60 kg (above), castor 0.300 kg,
RPLIDAR S3 0.115 kg, Gemini 336L 0.135 kg, ZLAC8015D 0.600 kg (an estimate in the ledger). The last four are the ledger
values; their data sheets are not in this repository.

## Parts not on the 2.0 base

- Legacy 1.x drive, replaced by work package M-02 (hub motors on rigid shaft-flat brackets): `MMP.03.00.00.000` wheel
  assembly and its parts `.001` to `.004`, `PT1.00.00.240` magnetic encoder with `PT1.00.00.241` to `.243`. Computed and
  listed with status `legacy`, not compared. The 2.0 motor brackets MEC-015 exist only as design-intent solids in
  openamrobot-docs; there is no released CAD to compare.
- `MMP.00.00.00.004 Plastic cover` and `PT1.00.00.032 Camera upper body`: not in the full assembly, not in the model.
- Assembly files (`MMP.01`, `.02`, `.03`, `.04`, `.05`, `.05-01`, `.07`): geometry only. Their rivet nuts, rivets,
  screws and washers are purchased hardware without a datasheet mass here (the ledger covers them as MEC-014, 0.6 kg
  estimate).

## Limits

- Design values from CAD and documents. The weighed mass and centre of gravity of the built base replace them.
- Powder coating (RAL 9016) and rivet nuts are not counted.
- The sheet-metal STEP solids are the bent parts. Bend relief and K-factor effects are in the CAD as modelled.
- The base_link substitution keeps the ledger for every part this report does not compute.

## Rerun

```bash
pip install cadquery-ocp numpy pyyaml
```

```bash
python tools/cad_massprops/massprops.py --docs ../openamrobot-docs
```
