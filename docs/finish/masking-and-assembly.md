# Masking and assembly sequence, mobile base

Order of work for the 2.0 prototype base. Finished parts are coated or printed before assembly;
purchased parts are never coated and are protected while other work goes on near them.

## 1. Before coating (per steel part)

1. Cut, bend and deburr per the drawing (edges broken 0.1 to 0.3 mm, drawing note 6).
2. Rivet nuts: set them before coating only if the thread is plugged (CAD README); otherwise set them
   after coating and touch up nothing.
3. Degrease and pretreat for polyester powder (coater's standard process).
4. Mask as listed below, then hang the part by a hole that is masked anyway.

| Part | Mask before powder coat |
|---|---|
| Side panels MMP.00.00.00.003 (RAL 7035) | rivet nut threads; bonding point; flange faces bolted to the base plate and supports |
| Front panel MMP.00.00.00.001 (RAL 7035) | E-stop hole bore and legend-plate seat; both MB7060 edge holes (27.5 mm) and their lock-nut clamp rings, both faces; TF-Luna centre hole; camera opening edges; rivet nut threads; bonding point |
| Rear panel MMP.00.00.00.002 (RAL 7035) | both MB7060 edge holes and clamp rings, both faces; 22.0 mm centre hole; any connector cut-out; rivet nut threads; bonding point |
| Cover MMP.01.00.00.001 (RAL 7016) | lift base plate footprint on the top face (size: verify, from the base plate drawing); the four M8 holes and washer faces on both faces; upper-body bonding point; rivet nut threads |
| Cover flanges MMP.01.00.00.002 (RAL 7016) | faces bolted to the cover and supports; rivet nut threads |
| Internal steel, kept RAL 9016 (base plate, centre bracket, supports, LiDAR support, electronics bracket) | as today: castor seats, hub motor bracket faces, battery restraint faces, LiDAR seat, main grounding point, threads |

Masking material: high-temperature polyester tape and silicone plugs or caps, removed after curing.
Hole bores are masked so that fits (E-stop 22 mm class, 3/4 inch NPS for the MB7060) are not reduced
by the coating (typically 60 to 80 micrometres per face; confirm with the coater).

## 2. Coating

1. Light grey RAL 7035 batch: side panels, front panel, rear panel.
2. Graphite RAL 7016 batch: cover and both cover flanges together, so that the upper cover matches.
3. Internal RAL 9016 parts: unchanged process per drawing note 8.
4. After curing, remove masks; check that bonding points read low resistance to the part (meter check,
   value set by the electrical owner).

## 3. Printed parts

Print in black PETG (close to RAL 9005), at least 4 perimeters and 40 % infill (mechanical BOM). Set
heat-set inserts after printing. No paint. Parts: camera mount, TF-Luna mounts (2), MB7060 mounts (4,
if the printed option is used), LiDAR spacer (if printed), motor driver mount.

## 4. Assembly order and protection

1. Base plate, castors with shims (MEC-016), centre bracket, supports: as today.
2. Hub motors: keep the tyres, shaft flats and brake housing clean; no tape on the brake.
3. Electronics on their brackets: Jetson, controller, driver, IMU. Keep heatsink and fan paths open.
4. Battery assembly on the rear deck.
5. Front and rear panels with sensors: fit the MB7060 sensors with their lock nuts, the TF-Luna and
   camera mounts, then the base E-stop. Do not tape over lenses or transducers; use the sensor's own
   caps or a loose bag while other work goes on.
6. Side panels.
7. LiDAR on its spacer. The scan window is never taped or filmed; protect it only with a loose cap that
   is removed before power-up.
8. Cover flanges and cover last. Before fitting the lift base plate, check the footprint mask is bare
   and the four M8 washer faces are clean.
9. Hand over to the upper-body sequence (openamr-upperbody-hw `docs/finish/masking-and-assembly.md`):
   lift base plate on the cover, then the column.

## 5. Final checks on the base

- E-stop red on yellow and RESET blue as delivered; labels and safety markings readable.
- No accent colour on the base; no orange or cyan within 150 mm of the E-stop or RESET (rule K1).
- All sensor apertures, the LiDAR scan band and cooling paths open.
- Bonding points bare and connected.
- No adhesive on any functional surface; no new holes.
