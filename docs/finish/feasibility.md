# Feasibility list, mobile base

Each item is in one category. An item leaves the list when its check is recorded (drawing revision,
measurement or written confirmation) in the PR that changes its status in `finishes.yaml`.

## Now (sources establish material and process)

| Item | Why it can proceed |
|---|---|
| Side panels MMP.00.00.00.003 in RAL 7035 matte powder | drawing gives EN 1.0114, 0.8 mm and an existing powder process; only the colour changes |
| Cover MMP.01.00.00.001 and flanges MMP.01.00.00.002 in RAL 7016 matte powder | same; the colour can be fixed now, the footprint mask waits for the base plate drawing (below) |
| Internal steel parts kept RAL 9016 as drawn | no change |
| Printed mounts in black PETG (camera, TF-Luna, motor driver mount) | mechanical BOM gives PETG; colour is a filament choice |
| Purchased parts as delivered | no operation |
| finishes.yaml read by the model | all 44 GLB node ids are mapped; checked by `tools/finish_tables.py --provenance` |

## Needs CAD or drawing confirmation

| Item | Exact check needed |
|---|---|
| Front and rear panel masks | confirm the committed PDF drawings MMP.00.00.00.001 and .002 match the Rev B panels in the v0.2 STEP: hole list, E-stop hole size, MB7060 edge holes 27.5 mm, rear 22.0 mm centre hole |
| Cover footprint mask | lift base plate outline and the orientation of the 190 x 300 mm M8 pattern (option B page, supplier CAD pending) |
| Bonding points | location of the chassis and upper-body bonding points (wiring drawing) |
| RESET button position | panel and position of XB4BW36B5 (not in the v0.2 CAD), to apply keep-out K1 |
| Electronics bracket MMP.04.00.00.002 | drawing with material and finish note (STEP only today) |
| Controller mount plate MMP.04.00.00.003 | drawing with material (6 mm plate, material not stated) |
| LiDAR spacer MMP.07.00.00.002 | printed (mechanical BOM) or aluminium (BOM row MEC-008 title) |
| Plastic cover MMP.00.00.00.004 | whether it is part of the 2.0 build (not in the v0.2 assembly) |
| Branding parts (BOM row MEC-017) | geometry and material in the cover drawings |
| Drawing note 8 | drawing owner revises note 8 on MMP.00.00.00.001 to .003, MMP.01.00.00.001 and .002 to the new RAL, or records the finish on a separate finish sheet |

## Needs supplier confirmation

| Item | Confirmation |
|---|---|
| RAL 7035 and RAL 7016 fine-texture matte polyester powder | coater confirms availability, film thickness per face and cure on 0.8 mm sheet without distortion |
| Black PETG close to RAL 9005 | filament colour checked against a RAL 9005 sample |
| MB7060 mounts | printed PETG or COTS retention set (BOM row MEC-011); a COTS set stays as delivered |

## Needs a fit check

| Item | Fit check |
|---|---|
| MB7060 in the coated panel | 3/4 inch NPS sensor and lock nut (MEC-021) in the masked 27.5 mm hole, both panels |
| E-stop in the coated front panel | XB4BS8445 and legend plate seat flat and do not rotate |
| Lift base plate on the coated cover | bare footprint, four M8 to torque, bonding resistance measured |
| Colour sample | one coated 0.8 mm coupon per colour viewed against the arm profile sample and the OpenArm parts in daylight |
