#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Stage the inputs of the finish preview renders (render_preview.mjs).

The same script lives in openamr-platform-hw and openamr-upperbody-hw (docs/finish/tools/).
It reads both finishes.yaml files, the upper-body configuration and the OpenArm 2.0 example
URDF, and writes <stage>/scene.json next to copies of the meshes. No geometry is changed:
the base is the GLB built by openamr-platform-sw tools/cad/step_to_description_meshes.py,
the arms are the openarm_description visual meshes at their zero pose, and the upper-body
parts the model does not have yet are drawn as labelled placeholders.

  python3 build_preview_scene.py --base-finishes <platform-hw>/docs/finish/finishes.yaml \
      --upper-finishes <upperbody-hw>/docs/finish/finishes.yaml \
      --glb <platform-sw>/build/base_visual.glb \
      --upper-config <upperbody-sw>/ros2/src/openamrobot_upperbody_description/config/upperbody_configuration.yaml \
      --openarm <openarm_description checkout> --stage <empty directory>
"""
import argparse
import json
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path

import yaml

BASE_LINK_HEIGHT = 0.098  # base_link above the floor (REP 105, FRAMES-REP105)


def colours(path):
    doc = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    out = {}
    for e in doc["entries"]:
        key = e["node_id"]
        if key:
            out[key] = {"id": e["id"], "hex": e["srgb_hex"], "finish": e["finish"], "status": e["status"]}
    return doc, out


def arm_links(urdf, side):
    """Zero-pose link origins and visuals of one arm, relative to openarm_<side>_base_link."""
    root = ET.parse(urdf).getroot()
    parent_of = {}
    for joint in root.findall("joint"):
        xyz = [float(v) for v in joint.find("origin").get("xyz").split()]
        parent_of[joint.find("child").get("link")] = (joint.find("parent").get("link"), xyz)
    base = f"openarm_{side}_base_link"
    links = []
    for link in root.findall("link"):
        name = link.get("name")
        if not name.startswith(f"openarm_{side}_"):
            continue
        pos, cur = [0.0, 0.0, 0.0], name
        while cur != base:
            parent, xyz = parent_of[cur]
            pos = [p + d for p, d in zip(pos, xyz)]
            cur = parent
        for visual in link.findall("visual"):
            mesh = visual.find("geometry/mesh")
            origin = visual.find("origin")
            links.append({
                "link": name,
                "mesh": mesh.get("filename").replace("package://openarm_description/", ""),
                "scale": [float(v) for v in mesh.get("scale", "1 1 1").split()],
                "xyz": [p + float(v) for p, v in zip(pos, origin.get("xyz", "0 0 0").split())],
            })
    return links


def main():
    ap = argparse.ArgumentParser()
    for name in ["--base-finishes", "--upper-finishes", "--glb", "--upper-config", "--openarm", "--stage"]:
        ap.add_argument(name, required=True)
    args = ap.parse_args()
    stage = Path(args.stage)
    stage.mkdir(parents=True, exist_ok=True)

    base_doc, base_colours = colours(args.base_finishes)
    upper_doc, upper_colours = colours(args.upper_finishes)
    cfg = yaml.safe_load(Path(args.upper_config).read_text(encoding="utf-8"))
    geo, col = cfg["geometry"], cfg["column"][cfg["baseline"]["column"]]
    pitch = cfg["head_pitch"][cfg["baseline"]["head_pitch"]]["pitch_down_deg"]

    shutil.copy(args.glb, stage / "base_visual.glb")
    urdf = Path(args.openarm) / "assets/robot/openarm_v2.0/urdf/example/v2.urdf"
    arms = {side: arm_links(urdf, side) for side in ("left", "right")}
    for side in arms.values():
        for item in side:
            target = stage / item["mesh"]
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(Path(args.openarm) / item["mesh"], target)

    # All positions in base_link (x forward, y left, z up), metres; lift 0, bp000, baseline pitch.
    z = lambda floor: floor - BASE_LINK_HEIGHT  # noqa: E731
    axis_x = 0.060 + cfg["base_plate"][cfg["baseline"]["base_plate"]]["column_axis_offset_x"]
    plate_top = geo["base_plate_top_z"]
    column_top = plate_top + col["retracted_length"]
    profile = geo["arm_profile"]
    profile_x = axis_x + profile["center_x_from_column_axis"]
    profile_bottom = column_top + geo["adapter_plate_thickness"]
    mount = geo["arm_mount"]
    lens = geo["head_camera_lens"]
    shoulder = column_top + mount["z_above_column_top"]
    scene = {
        "palette": base_doc["palette"],
        "base_colours": base_colours,
        "upper_colours": upper_colours,
        "pitch_down_deg": pitch,
        "boxes": [
            # placeholders: the model has no geometry for these parts yet
            {"node": "lift_base_plate", "placeholder": True, "size": [0.320, 0.210, 0.010],
             "centre": [axis_x, 0.0, z(plate_top - 0.005)],
             "why": "outline pending; drawn as the 300 x 190 mm bolt pattern plus 10 mm"},
            {"node": "lift_column", "placeholder": True, "size": [0.240, 0.240, col["retracted_length"]],
             "centre": [axis_x, 0.0, z(plate_top + col["retracted_length"] / 2)],
             "why": "240 mm side fore-aft from the register; lateral width not established"},
            {"node": "adapter_plate", "placeholder": False, "size": [0.360, 0.100, geo["adapter_plate_thickness"]],
             "centre": [axis_x + 0.060, 0.0, z(column_top + geo["adapter_plate_thickness"] / 2)],
             "why": "360 x 100 x 10 mm, BOM row MEC-003 description"},
            {"node": "arm_profile", "placeholder": False,
             "size": [profile["size_x"], profile["size_y"], profile["length"]],
             "centre": [profile_x, 0.0, z(profile_bottom + profile["length"] / 2)],
             "why": "arm_profile_link visual box of the upper-body description"},
            {"node": "head_camera", "placeholder": False, "size": [0.0265, 0.1245, 0.0305],
             "lens": [profile_x + lens["x_ahead_of_arm_mount"], lens["y"],
                      z(shoulder + lens["z_above_arm_mount"])],
             "why": "ZED Mini outline 124.5 x 30.5 x 26.5 mm (Stereolabs), lens line on its front face"},
        ],
        "slot_strips": [
            {"node": "slot_cover_left", "y": profile["size_y"] / 2, "x": profile_x + 0.045,
             "z_bottom": z(profile_bottom + 0.005)},
            {"node": "slot_cover_right", "y": -profile["size_y"] / 2, "x": profile_x + 0.045,
             "z_bottom": z(profile_bottom + 0.005)},
        ],
        "arm_mounts": {"left": [profile_x, mount["y"], z(shoulder)],
                       "right": [profile_x, -mount["y"], z(shoulder)]},
        "arms": arms,
    }
    (stage / "scene.json").write_text(json.dumps(scene, indent=1), encoding="utf-8")
    print(f"staged {stage}: column top {column_top:.3f} m, shoulder {shoulder:.3f} m above the floor")


if __name__ == "__main__":
    main()
