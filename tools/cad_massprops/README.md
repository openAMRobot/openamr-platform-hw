# CAD mass properties

`massprops.py` computes the physical mass properties of the OpenAMRobot 2.0 mobile base from its STEP files and compares
them with the mass ledger of the roadmap model in openamrobot-docs. Results and the report are in the
[mass properties folder](../../docs/mass-properties/report.md).

## Files

| File | What |
|---|---|
| `massprops.py` | The script. Reads the STEP files, computes volume, box, centre of mass and inertia, assigns materials, rolls up the full assembly, compares with the ledger. |
| `materials.yaml` | Materials with density and source, every part with its material source, purchased parts with their datasheet mass, the assembly frame and the one placement correction. |

## Run

```bash
pip install cadquery-ocp numpy pyyaml
```

```bash
python tools/cad_massprops/massprops.py --docs ../openamrobot-docs
```

`--docs` points to a checkout of openamrobot-docs. The script reads `scripts/roadmap_model/mass_ledger.yaml`,
`link_map.yaml`, `facts.yaml`, `docs/assets/roadmap/model/mass_export.yaml` and `base_glb.js` there and writes nothing
there. Without `--docs` only the CAD results are written. The run takes about 2.5 minutes; most of it is the 139 MB full
assembly STEP, which the script unzips to a temporary folder.

Tested with cadquery-ocp 8.0.1.1 and Python 3.13.

## Method

- STEP reading: OCP `STEPControl_Reader` for part files, `STEPCAFControl_Reader` (XCAF) for the full assembly tree and
  placements.
- Length unit: `STEPControl_Controller.Init_s()` first, then `Interface_Static.SetCVal_s("xstep.cascade.unit", "M")`.
  The script stops if the setting is not accepted. Without the controller initialisation the first `SetCVal_s` call
  returns False and the first file read stays in millimetres. That file then looks 1000 times too large.
- Unit check: the sorted box of every part is compared with the overall size on its drawing (`drawing_mm` in
  `materials.yaml`). A ratio of 1000, 0.001, 25.4 or 1/25.4 is corrected in the computation only and the file is listed
  for re-export. Any other mismatch is reported and not corrected.
- Properties: `BRepGProp.VolumeProperties_s` gives volume, centre of mass and the inertia tensor per unit density about
  the centre of mass. The box comes from `BRepBndLib.AddOptimal_s` with `Bnd_Box.CornerMin` and `CornerMax`
  (`Bnd_Box.Get` does not work in this binding).
- Inertia convention: the tensor, with Ixy = minus the integral of x y dm. This is the URDF convention.
- Mass: volume x density for fabricated and printed parts with a documented material. Purchased parts take the
  datasheet or BOM mass. A purchased part STEP is used for geometry and, marked as an estimate, for an inertia at uniform
  density scaled to the datasheet mass.
- Assembly: every leaf of the full assembly STEP is matched to a part by the `leaf` pattern in `materials.yaml`, placed
  with its accumulated transform, and summed with the parallel-axis theorem. The result is given in the CAD frame, in
  base_footprint and in base_link.

## Rules

- A material is assigned only when a drawing, the BOM or M-01 names it. The source is in `materials.yaml` and in every
  output row.
- No document names the material: material `unknown`, no mass. The volume and the unit-density inertia (`j*` columns,
  m5) are still given, so a mass follows directly once the material is known.
- Values that are not from a document for that exact part are marked `estimate`.
- The material property "Celik" (steel, 7850 kg/m3) in the Autodesk-exported STEP files is the CAD default. It is also on
  parts that the BOM names PETG. It is not used as a source.
- Nothing in openamrobot-docs, in the STEP files or in any URDF is changed.

## Adding or changing a part

Edit `materials.yaml`: give the file, the material key and the document that names the material, the drawing size for
the unit check, the ledger component it is compared with and the leaf pattern in the full assembly. Then rerun.
