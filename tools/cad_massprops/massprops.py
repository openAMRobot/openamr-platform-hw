#!/usr/bin/env python3
"""CAD mass properties of the OpenAMRobot 2.0 mobile base, compared with the roadmap model mass ledger.

Reads the STEP files of mechanical/cad/production_files, the hub motor STEP and the full assembly STEP with OpenCASCADE
(cadquery-ocp), assigns materials from materials.yaml (every assignment with its source), and writes:

  docs/mass-properties/part_massprops.csv    one row per part file: volume, box, centre of mass, inertia, material, mass
  docs/mass-properties/link_comparison.csv   part, BOM line and URDF link comparison with the roadmap model ledger
  docs/mass-properties/massprops.json        the same numbers and the assembly roll-up, for report.md and other tools

The comparison needs a checkout of openamrobot-docs (--docs). It reads mass_ledger.yaml, mass_export.yaml, link_map.yaml and
base_glb.js there and changes nothing.

Usage:
  pip install cadquery-ocp numpy pyyaml
  python tools/cad_massprops/massprops.py --docs ../openamrobot-docs

Units: SI (m, kg, kg m2) unless a column says mm or cm3. Inertia is the tensor about the centre of mass
(Ixy = -integral of x y dm, the URDF convention).
"""
import argparse
import base64
import csv
import json
import math
import os
import re
import struct
import sys
import tempfile
import zipfile

import numpy as np
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
PROD = os.path.join(REPO, "mechanical", "cad", "production_files")

# ------------------------------------------------------------------ OpenCASCADE

_OCC = {}


def occ():
    """Import OCP once and set the STEP length unit to metres.

    The STEP controller must be initialised before xstep.cascade.unit exists. Without STEPControl_Controller.Init_s() the
    first Interface_Static.SetCVal_s call returns False and the first file read stays in millimetres (a part then looks
    1000 times too large). The call result is checked here.
    """
    if _OCC:
        return _OCC
    from OCP.STEPControl import STEPControl_Controller, STEPControl_Reader
    from OCP.Interface import Interface_Static
    from OCP.IFSelect import IFSelect_RetDone
    from OCP.GProp import GProp_GProps
    from OCP.BRepGProp import BRepGProp
    from OCP.Bnd import Bnd_Box
    from OCP.BRepBndLib import BRepBndLib
    from OCP.TopExp import TopExp_Explorer
    from OCP.TopAbs import TopAbs_SOLID
    from OCP.STEPCAFControl import STEPCAFControl_Reader
    from OCP.TDocStd import TDocStd_Document
    from OCP.TCollection import TCollection_ExtendedString
    from OCP.XCAFDoc import XCAFDoc_DocumentTool, XCAFDoc_ShapeTool
    from OCP.TDF import TDF_Label, TDF_ChildIterator
    from OCP.TDataStd import TDataStd_Name
    from OCP.TopLoc import TopLoc_Location
    from OCP.gp import gp_Trsf, gp_Vec

    STEPControl_Controller.Init_s()
    if not Interface_Static.SetCVal_s("xstep.cascade.unit", "M") or Interface_Static.CVal_s("xstep.cascade.unit") != "M":
        sys.exit("cannot set xstep.cascade.unit to M")
    _OCC.update(locals())
    return _OCC


def read_step(path):
    o = occ()
    r = o["STEPControl_Reader"]()
    if r.ReadFile(path) != o["IFSelect_RetDone"]:
        raise RuntimeError("cannot read " + path)
    r.TransferRoots()
    return r.OneShape()


def shape_props(shape):
    """Volume (m3), centre of mass (m), inertia tensor per unit density about the centre of mass (m5), box (m), solids."""
    o = occ()
    p = o["GProp_GProps"]()
    o["BRepGProp"].VolumeProperties_s(shape, p)
    vol = p.Mass()
    c = p.CentreOfMass()
    m = p.MatrixOfInertia()
    J = np.array([[m.Value(i, j) for j in (1, 2, 3)] for i in (1, 2, 3)])
    b = o["Bnd_Box"]()
    o["BRepBndLib"].AddOptimal_s(shape, b, False, False)
    if b.IsVoid():
        return None
    lo, hi = b.CornerMin(), b.CornerMax()   # Bnd_Box.Get does not work in this binding
    n, e = 0, o["TopExp_Explorer"](shape, o["TopAbs_SOLID"])
    while e.More():
        n += 1
        e.Next()
    return {"vol": vol, "com": np.array([c.X(), c.Y(), c.Z()]), "J": J,
            "lo": np.array([lo.X(), lo.Y(), lo.Z()]), "hi": np.array([hi.X(), hi.Y(), hi.Z()]), "solids": n}


def scale_props(p, s):
    return {**p, "vol": p["vol"] * s ** 3, "com": p["com"] * s, "J": p["J"] * s ** 5, "lo": p["lo"] * s, "hi": p["hi"] * s}


def unit_check(p, drawing_mm):
    """Compare the sorted box with the sorted drawing size. Returns (scale factor to apply, status text)."""
    box = np.sort((p["hi"] - p["lo"]) * 1000)[::-1]
    if not drawing_mm:
        big = box.max()
        if big > 2000 or big < 1:
            return None, "box %.1f mm is outside 1 mm to 2 m and no drawing size is given: check the length unit" % big
        return 1.0, "no drawing size; box within 1 mm to 2 m"
    ref = np.sort(np.array(drawing_mm, float))[::-1]
    r = float(np.median(box / ref))
    if abs(r - 1) < 0.03:
        return 1.0, "box matches the drawing (ratio %.3f)" % r
    for k, name in ((1000.0, "m read as mm"), (0.001, "mm read as m"), (25.4, "inch read as mm"), (1 / 25.4, "mm read as inch")):
        if abs(r / k - 1) < 0.03:
            return 1.0 / k, "box is %.4g x the drawing (%s): corrected by %.6g in this computation; re-export the STEP" % (r, name, 1.0 / k)
    return None, "box does not match the drawing (ratio %.3f): not corrected" % r


def name_of(label):
    o = occ()
    a = o["TDataStd_Name"]()
    return a.Get().ToExtString() if label.FindAttribute(o["TDataStd_Name"].GetID_s(), a) else ""


def assembly_leaves(path):
    """Every leaf shape of an assembly STEP with its accumulated placement: [(name, path, located shape, part shape)]."""
    o = occ()
    ST = o["XCAFDoc_ShapeTool"]
    doc = o["TDocStd_Document"](o["TCollection_ExtendedString"]("XmlOcaf"))
    r = o["STEPCAFControl_Reader"]()
    r.SetNameMode(True)
    if r.ReadFile(path) != o["IFSelect_RetDone"]:
        raise RuntimeError("cannot read " + path)
    r.Transfer(doc)
    st = o["XCAFDoc_DocumentTool"].ShapeTool_s(doc.Main())

    def children(lab):
        it, out = o["TDF_ChildIterator"](lab, False), []
        while it.More():
            out.append(it.Value())
            it.Next()
        return out

    leaves = []

    def walk(lab, loc, trail):
        nm = name_of(lab)
        if ST.IsAssembly_s(lab):
            for c in children(lab):
                if ST.IsComponent_s(c):
                    ref = o["TDF_Label"]()
                    ST.GetReferredShape_s(c, ref)
                    walk(ref, loc.Multiplied(ST.GetLocation_s(c)), trail + [nm])
        else:
            part = ST.GetShape_s(lab)
            leaves.append((nm, trail, part.Moved(loc), part))

    for lab in children(st.Label()):
        if ST.IsFree_s(lab) and ST.IsShape_s(lab):
            walk(lab, o["TopLoc_Location"](), [])
    return leaves


# ------------------------------------------------------------------ mass helpers

def mass_item(p, rho):
    return {"m": p["vol"] * rho, "c": p["com"], "I": p["J"] * rho}


def combine(items):
    """Sum of mass items {m, c, I (about own centre)}: total mass, centre, tensor about the total centre."""
    M = sum(i["m"] for i in items)
    c = sum(i["m"] * i["c"] for i in items) / M
    I = np.zeros((3, 3))
    for i in items:
        d = i["c"] - c
        I += i["I"] + i["m"] * (np.dot(d, d) * np.eye(3) - np.outer(d, d))
    return {"m": M, "c": c, "I": I}


def to_frame(item, R, t):
    R = np.array(R, float)
    return {"m": item["m"], "c": R @ item["c"] + np.array(t, float), "I": R @ item["I"] @ R.T}


def principal(I):
    w, v = np.linalg.eigh(I)
    return w, v


def r(x, n=6):
    return None if x is None else float(round(float(x), n))


# ------------------------------------------------------------------ roadmap model inputs (openamrobot-docs, read only)

def glb_nodes(path, base_link_z):
    """Base GLB nodes of the roadmap model as {id: (vertices in base_footprint, faces)} (same parse as frames.py)."""
    s = open(path, encoding="utf-8").read()
    t = base64.b64decode(s[s.index('"') + 1:s.rindex('"')].replace(".", ""))
    jl = struct.unpack("<I", t[12:16])[0]
    doc = json.loads(t[20:20 + jl])
    b0 = 28 + jl
    out = {}
    for n in doc["nodes"]:
        if "mesh" not in n:
            continue
        ex = n.get("extras", {"id": n["name"]})
        vs, fs, off = [], [], 0
        for p in doc["meshes"][n["mesh"]]["primitives"]:
            a = doc["accessors"][p["attributes"]["POSITION"]]
            bv = doc["bufferViews"][a["bufferView"]]
            o = b0 + bv.get("byteOffset", 0)
            v = np.frombuffer(t[o:o + bv["byteLength"]], dtype="<f4").reshape(-1, 3).astype(float)
            ia = doc["accessors"][p["indices"]]
            ibv = doc["bufferViews"][ia["bufferView"]]
            o = b0 + ibv.get("byteOffset", 0)
            idx = np.frombuffer(t[o:o + ibv["byteLength"]], dtype="<u2" if ia["componentType"] == 5123 else "<u4").reshape(-1, 3)
            fs.append(idx + off)
            vs.append(v)
            off += len(v)
        v = np.vstack(vs)
        v[:, 2] += base_link_z
        out[ex["id"]] = (v, np.vstack(fs))
    return out


def mesh_vol_com(v, f):
    tri = v[f]
    a, b, c = tri[:, 0], tri[:, 1], tri[:, 2]
    dv = np.einsum("ij,ij->i", a, np.cross(b, c)) / 6
    V = dv.sum()
    com = ((a + b + c) / 4 * dv[:, None]).sum(0) / V
    return abs(V), com


def load_docs(docs):
    p = lambda *a: os.path.join(docs, *a)
    d = {"ledger": yaml.safe_load(open(p("scripts", "roadmap_model", "mass_ledger.yaml"))),
         "export": yaml.safe_load(open(p("docs", "assets", "roadmap", "model", "mass_export.yaml"))),
         "link_map": yaml.safe_load(open(p("scripts", "roadmap_model", "link_map.yaml")))}
    facts = yaml.safe_load(open(p("scripts", "roadmap_model", "facts.yaml")))
    d["base_link_z"] = float(facts["base_link_z"])
    d["glb"] = glb_nodes(p("docs", "assets", "roadmap", "model", "base_glb.js"), d["base_link_z"])
    return d


# ------------------------------------------------------------------ main

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--materials", default=os.path.join(HERE, "materials.yaml"))
    ap.add_argument("--docs", help="openamrobot-docs checkout for the ledger comparison (read only)")
    ap.add_argument("--full-assembly", help="full assembly STEP or its zip (default: materials.yaml assembly.file)")
    ap.add_argument("--out", default=os.path.join(REPO, "docs", "mass-properties"))
    a = ap.parse_args()
    cfg = yaml.safe_load(open(a.materials, encoding="utf-8"))
    mats = cfg["materials"]
    os.makedirs(a.out, exist_ok=True)
    flags_tol_rel, flags_tol_abs = 0.05, 0.050
    result = {"parts": [], "assemblies": [], "purchased": [], "rollup": {}, "comparison": [], "reexport": [], "notes": []}

    def density(mat):
        if mat in mats:
            return mats[mat]["density_kg_m3"], mats[mat]["density_source"], bool(mats[mat].get("estimate"))
        return None, "", False

    # ---- 1. every part file
    part_props = {}
    for e in cfg["parts"]:
        path = os.path.join(PROD, e["file"])
        p0 = shape_props(read_step(path))
        s, status = unit_check(p0, e.get("drawing_mm"))
        p = scale_props(p0, s) if s not in (None, 1.0) else p0
        if s not in (None, 1.0):
            result["reexport"].append({"file": "mechanical/cad/production_files/" + e["file"], "reason": status})
        rho, rsrc, rest = density(e["material"])
        mass = p["vol"] * rho if rho else None
        part_props[e["part"]] = p
        result["parts"].append({"cfg": e, "p": p, "unit": status, "scale": s, "rho": rho, "rho_src": rsrc,
                                "mass": mass, "estimate": rest or e["material"] == "unknown"})
        print("%-22s %-28s V=%9.2f cm3 m=%s  %s" % (e["part"], e["name"][:28], p["vol"] * 1e6,
                                                   "%.4f kg" % mass if mass else "-", status), flush=True)
    for e in cfg.get("assemblies", []):
        p = shape_props(read_step(os.path.join(PROD, e["file"])))
        result["assemblies"].append({"cfg": e, "p": p})

    # ---- 2. purchased parts (datasheet mass; STEP for an inertia estimate only)
    for e in cfg["purchased"]:
        row = {"cfg": e, "p": None, "I": None}
        if e.get("file"):
            p = shape_props(read_step(os.path.join(REPO, e["file"])))
            row["p"] = p
            row["I"] = p["J"] * e["mass_kg"] / p["vol"]   # uniform density scaled to the datasheet mass (estimate)
        result["purchased"].append(row)

    # ---- 3. assembly roll-up from the full assembly STEP
    acfg = cfg["assembly"]
    fa = a.full_assembly or os.path.join(REPO, acfg["file"])
    tmp = None
    if fa.lower().endswith(".zip"):
        tmp = tempfile.TemporaryDirectory()
        with zipfile.ZipFile(fa) as z:
            name = [n for n in z.namelist() if n.lower().endswith((".step", ".stp"))][0]
            z.extract(name, tmp.name)
            fa = os.path.join(tmp.name, name)
    print("reading the full assembly (about 2 minutes)", flush=True)
    leaves = assembly_leaves(fa)
    o = occ()
    by_part = {e["part"]: e for e in cfg["parts"]}
    placed, unmatched_void = [], []
    for nm, trail, shp, part in leaves:
        for e in cfg["parts"]:
            if e.get("leaf") and re.search(e["leaf"], nm):
                ov = acfg.get("placement_overrides", {}).get(e["part"])
                corrected = False
                if ov:
                    tr = o["gp_Trsf"]()
                    tr.SetTranslation(o["gp_Vec"](*ov["translation_m"]))
                    orig = shape_props(shp)
                    shp = part.Moved(o["TopLoc_Location"](tr))
                    corrected = orig["lo"].tolist()
                pp = shape_props(shp)
                if pp is None:
                    unmatched_void.append({"part": e["part"], "leaf": nm})
                    break
                placed.append({"part": e["part"], "leaf": nm, "p": pp, "corrected_from_lo": corrected})
                break
    R, t = acfg["to_base_footprint"]["rotation"], acfg["to_base_footprint"]["translation_m"]
    zbl = acfg["base_link_z_m"]
    t_bl = (np.array(t, float) - [0, 0, zbl]).tolist()
    items, excluded = [], []
    for pl in placed:
        e = by_part[pl["part"]]
        rho, _, _ = density(e["material"])
        vol_file = part_props[e["part"]]["vol"]
        pl["vol_matches_file"] = abs(pl["p"]["vol"] / vol_file - 1) < 0.005
        if e["status"] not in acfg["rollup_status"]:
            continue
        if not rho:
            excluded.append(pl)
            continue
        it = mass_item(pl["p"], rho)
        pl["item_cad"] = it
        pl["item_bl"] = to_frame(it, R, t_bl)
        items.append(pl)
    ru = {}
    groups = {"MEC-001 sheet-metal chassis": lambda e: e.get("bom") == "MEC-001",
              "all placed parts with a known material": lambda e: True}
    for gname, sel in groups.items():
        its = [pl for pl in items if sel(by_part[pl["part"]])]
        if not its:
            continue
        cad = combine([pl["item_cad"] for pl in its])
        bl = to_frame(cad, R, t_bl)
        ru[gname] = {"n": len(its), "parts": sorted({pl["part"] for pl in its}), "cad": cad, "base_link": bl,
                     "base_footprint": to_frame(cad, R, t)}
    result["rollup"] = ru
    result["placed"] = placed
    result["excluded"] = excluded
    result["void"] = unmatched_void
    result["frame"] = {"R": R, "t_bf": t, "t_bl": t_bl}

    # ---- 4. comparison with the roadmap model
    if a.docs:
        D = load_docs(a.docs)
        exp = D["export"]["groups"]["base"]["links"]
        items_bl = {i["component"]: i for i in exp["base_link"]["items"]}
        comp = []

        def flag(led, cad):
            if led is None or cad is None:
                return ""
            d = cad - led
            return "yes" if abs(d) > flags_tol_abs or (led and abs(d) / led > flags_tol_rel) else "no"

        def add(level, ident, name, led, cad, basis, note, led_src="", **kw):
            d = None if led is None or cad is None else cad - led
            comp.append({"level": level, "id": ident, "name": name, "ledger_kg": r(led, 4), "cad_kg": r(cad, 4),
                         "diff_kg": r(d, 4), "diff_pct": r(100 * d / led, 1) if d is not None and led else None,
                         "flag": flag(led, cad), "cad_basis": basis, "ledger_source": led_src, "note": note, **kw})

        # per part. MEC-001 parts: the ledger mass is the roadmap mesh volume x 7850 (analyse.py), one value per GLB node.
        per_line_items = {"MEC-008": ["lidar_support", "lidar_spacer"], "MEC-009": ["camera_mount"],
                          "MEC-010": ["tof_mount"], "MEC-011": ["ultrasonic_mount"]}
        placed_com = {}
        for pl in placed:
            placed_com.setdefault(pl["part"], []).append(np.array(R) @ pl["p"]["com"] + np.array(t))
        for row in result["parts"]:
            e = row["cfg"]
            if e["status"] != "on_2_0":
                continue
            qty = e["qty"]
            cad_each = row["mass"]
            for k, node in enumerate(e.get("ledger", [])):
                led, src, glb_com, glb_vol = None, "", None, None
                if node in D["glb"]:
                    glb_vol, glb_com = mesh_vol_com(*D["glb"][node])
                if e.get("bom") == "MEC-001" and glb_vol is not None:
                    led, src = glb_vol * 7850, "roadmap mesh volume x 7850 (method of analyse.py; MEC-001 total in mass_export.yaml)"
                elif node in items_bl:
                    led, src = items_bl[node]["mass_kg"], "mass_export.yaml base_link item: " + str(items_bl[node].get("source"))
                else:
                    for bid, comps in per_line_items.items():
                        if e.get("bom") == bid:
                            for cname in comps:
                                if cname in items_bl and node.startswith(cname.split("_")[0]):
                                    led = items_bl[cname]["mass_kg"] / qty
                                    src = "mass_export.yaml base_link item %s %.3f kg / %d" % (cname, items_bl[cname]["mass_kg"], qty)
                if led is None and e.get("bom") is None:
                    src = "not in the mass ledger (no BOM line)"
                cad_com = None
                pcs = placed_com.get(e["part"], [])
                if glb_com is not None and pcs:
                    cad_com = min(pcs, key=lambda c: np.linalg.norm(c - glb_com))
                note = []
                if glb_vol is not None:
                    note.append("roadmap mesh volume %.2f cm3, STEP %.2f cm3" % (glb_vol * 1e6, row["p"]["vol"] * 1e6))
                if cad_each is None:
                    note.append("material unknown: no CAD mass")
                if row["estimate"] and cad_each is not None:
                    note.append("estimate (" + e["material"] + ")")
                add("part", e["part"], "%s (%s)" % (e["name"], node), led, cad_each,
                    "STEP volume x %s %s kg/m3" % (e["material"], row["rho"]) if cad_each else "none", "; ".join(note), src,
                    com_shift_mm=r(np.linalg.norm(cad_com - glb_com) * 1000, 1) if cad_com is not None else None)
        # BOM line MEC-001 as a whole
        m001 = items_bl["chassis"]["mass_kg"]
        c001 = sum(rw["mass"] * rw["cfg"]["qty"] for rw in result["parts"] if rw["cfg"].get("bom") == "MEC-001")
        nodes001 = [n for rw in result["parts"] if rw["cfg"].get("bom") == "MEC-001" for n in rw["cfg"].get("ledger", [])]
        rec = sum(mesh_vol_com(*D["glb"][n])[0] * 7850 for n in nodes001 if n in D["glb"])
        add("bom_line", "MEC-001", "Robot 2.0 chassis/deck and panels (13 parts)", m001, c001,
            "13 STEP parts x steel EN 1.0114 (drawings)",
            "ledger = roadmap meshes x 7850; the per-part rows above sum to %.3f kg" % rec, "mass_export.yaml base_link item chassis")
        led008 = items_bl["lidar_support"]["mass_kg"] + items_bl["lidar_spacer"]["mass_kg"]
        sup = [rw for rw in result["parts"] if rw["cfg"]["part"] == "MMP.07.00.00.001"][0]["mass"]
        add("bom_line", "MEC-008", "LiDAR support and spacer", led008, None, "support %.4f kg (steel); spacer material unknown" % sup,
            "no total: spacer material unknown", "mass_export.yaml lidar_support + lidar_spacer (estimate)")
        # hub motor
        hm = [p for p in result["purchased"] if p["cfg"]["id"] == "DRV-001"][0]
        led_hm = D["ledger"]["lines"]["DRV-001"]["unit_kg"]
        add("bom_line", "DRV-001", "Hub motor (each)", led_hm, hm["cfg"]["mass_kg"], "datasheet (not CAD volume)",
            "B2 V1.01 drawing has no weight; value pending weighing", "mass_ledger.yaml: " + D["ledger"]["lines"]["DRV-001"]["src"])
        # links
        bl = exp["base_link"]
        sub = {"chassis": None, "lidar_support": None, "camera_mount": None, "tof_mount": None, "ultrasonic_mount": None}
        new_by_comp = {"chassis": [pl for pl in items if by_part[pl["part"]].get("bom") == "MEC-001"],
                       "lidar_support": [pl for pl in items if pl["part"] == "MMP.07.00.00.001"],
                       "tof_mount": [pl for pl in items if pl["part"] == "MMP.00.00.00.005"],
                       "ultrasonic_mount": [pl for pl in items if pl["part"] == "MMP.00.00.00.006"]}
        cam = [rw for rw in result["parts"] if rw["cfg"]["part"] == "MMP.01.00.00.003"][0]
        old_items, new_items = [], []
        for cname in sub:
            it = items_bl[cname]
            s_ = np.array(it["size_m"], float)
            Ib = it["mass_kg"] / 12 * np.diag([s_[1] ** 2 + s_[2] ** 2, s_[0] ** 2 + s_[2] ** 2, s_[0] ** 2 + s_[1] ** 2])
            old_items.append({"m": it["mass_kg"], "c": np.array(it["com_m"]) - [0, 0, D["base_link_z"]], "I": Ib})
            if cname in new_by_comp:
                new_items += [pl["item_bl"] for pl in new_by_comp[cname]]
            elif cname == "camera_mount":
                # placement of the camera mount is void in the full assembly: keep the ledger position, CAD mass (PETG)
                new_items.append({"m": cam["mass"], "c": np.array(it["com_m"]) - [0, 0, D["base_link_z"]], "I": np.zeros((3, 3))})
        Mo = bl["mass_kg"]
        co = np.array(bl["com_m"])
        Io = np.diag([bl["inertia_kgm2"][k] for k in ("ixx", "iyy", "izz")])
        # rest of the link = ledger link minus the replaced items (diagonal box inertia, about the old centre)
        rest_m = Mo - sum(i["m"] for i in old_items)
        rest_c = (Mo * co - sum(i["m"] * i["c"] for i in old_items)) / rest_m
        Irest_o = Io.copy()
        for i in old_items:
            d = i["c"] - co
            Irest_o -= i["I"] + i["m"] * (np.dot(d, d) * np.eye(3) - np.outer(d, d))
        d = rest_c - co
        Irest = Irest_o - rest_m * (np.dot(d, d) * np.eye(3) - np.outer(d, d))
        new = combine([{"m": rest_m, "c": rest_c, "I": Irest}] + new_items)
        add("link", "base_link", "base_link with the CAD masses substituted", Mo, new["m"],
            "ledger link with MEC-001, MEC-008 support, MEC-009, MEC-010, MEC-011 replaced by CAD values",
            "rest of the link unchanged (ledger box inertia); parts with unknown material not added",
            "mass_export.yaml base_link",
            ledger_com_m=[r(x, 4) for x in co], cad_com_m=[r(x, 4) for x in new["c"]],
            ledger_inertia_diag=[r(x, 5) for x in np.diag(Io)], cad_inertia=[[r(x, 5) for x in row] for row in new["I"]])
        for wl in ("left_wheel_link", "right_wheel_link"):
            Iw = hm["I"]   # STEP frame: spin axis x; link frame: spin axis y
            P = np.array([[0, 1, 0], [1, 0, 0], [0, 0, 1]], float)
            Iwl = P @ Iw @ P.T
            add("link", wl, "hub motor on its wheel link", exp[wl]["mass_kg"], hm["cfg"]["mass_kg"],
                "datasheet mass; inertia: B2 STEP uniform density scaled to the mass (estimate)",
                "whole motor on the spinning link as in the ledger (conflict M4)", "mass_export.yaml " + wl,
                ledger_com_m=exp[wl]["com_m"], cad_com_m=None,
                ledger_inertia_diag=[exp[wl]["inertia_kgm2"][k] for k in ("ixx", "iyy", "izz")],
                cad_inertia=[[r(x, 5) for x in row] for row in Iwl])
        for lk in ("fl_caster_link", "fr_caster_link", "bl_caster_link", "br_caster_link", "fl_wheel_link", "fr_wheel_link",
                   "bl_wheel_link", "br_wheel_link", "lidar_link"):
            add("link", lk, "purchased part only", exp[lk]["mass_kg"], None, "no CAD mass (purchased part, datasheet mass)",
                "not compared", "mass_export.yaml " + lk)
        result["comparison"] = comp
        result["base_link_new"] = new

    # ---- outputs
    write_outputs(a.out, result, mats)
    if tmp:
        tmp.cleanup()


def write_outputs(out, res, mats):
    cols = ["part", "name", "file", "status", "qty_on_2_0", "bom", "material", "material_source", "density_kg_m3", "density_source",
            "solids", "volume_cm3", "box_x_mm", "box_y_mm", "box_z_mm", "unit_check", "com_x_mm", "com_y_mm", "com_z_mm",
            "mass_kg", "mass_basis", "estimate", "ixx_kgm2", "iyy_kgm2", "izz_kgm2", "ixy_kgm2", "ixz_kgm2", "iyz_kgm2",
            "jxx_m5", "jyy_m5", "jzz_m5", "jxy_m5", "jxz_m5", "jyz_m5"]
    rows = []

    def base_row(part, name, file, p):
        box = (p["hi"] - p["lo"]) * 1000
        J = p["J"]
        return {"part": part, "name": name, "file": file, "solids": p["solids"], "volume_cm3": r(p["vol"] * 1e6, 3),
                "box_x_mm": r(box[0], 2), "box_y_mm": r(box[1], 2), "box_z_mm": r(box[2], 2),
                "com_x_mm": r(p["com"][0] * 1000, 2), "com_y_mm": r(p["com"][1] * 1000, 2), "com_z_mm": r(p["com"][2] * 1000, 2),
                "jxx_m5": "%.6e" % J[0, 0], "jyy_m5": "%.6e" % J[1, 1], "jzz_m5": "%.6e" % J[2, 2],
                "jxy_m5": "%.6e" % J[0, 1], "jxz_m5": "%.6e" % J[0, 2], "jyz_m5": "%.6e" % J[1, 2]}

    for row in res["parts"]:
        e, p = row["cfg"], row["p"]
        d = base_row(e["part"], e["name"], "mechanical/cad/production_files/" + e["file"], p)
        d.update({"status": e["status"], "qty_on_2_0": e["qty"], "bom": e.get("bom", ""), "material": e["material"],
                  "material_source": e["material_source"], "density_kg_m3": row["rho"] or "", "density_source": row["rho_src"],
                  "unit_check": row["unit"], "estimate": "yes" if row["estimate"] else "no"})
        if row["mass"]:
            I = p["J"] * row["rho"]
            d.update({"mass_kg": r(row["mass"], 5), "mass_basis": "STEP volume x density",
                      "ixx_kgm2": "%.6e" % I[0, 0], "iyy_kgm2": "%.6e" % I[1, 1], "izz_kgm2": "%.6e" % I[2, 2],
                      "ixy_kgm2": "%.6e" % I[0, 1], "ixz_kgm2": "%.6e" % I[0, 2], "iyz_kgm2": "%.6e" % I[1, 2]})
        else:
            d.update({"mass_kg": "", "mass_basis": "none: material unknown"})
        rows.append(d)
    for row in res["assemblies"]:
        e, p = row["cfg"], row["p"]
        d = base_row(e["part"], e["name"], "mechanical/cad/production_files/" + e["file"], p)
        d.update({"status": "assembly", "material": "mixed", "material_source": "assembly file: geometry only",
                  "mass_basis": "none: assembly (mass from its parts)", "estimate": "", "unit_check": "assembly"})
        rows.append(d)
    for row in res["purchased"]:
        e, p = row["cfg"], row["p"]
        if p is not None:
            d = base_row(e["id"], e["name"], e["file"], p)
            I = row["I"]
            d.update({"ixx_kgm2": "%.6e" % I[0, 0], "iyy_kgm2": "%.6e" % I[1, 1], "izz_kgm2": "%.6e" % I[2, 2],
                      "ixy_kgm2": "%.6e" % I[0, 1], "ixz_kgm2": "%.6e" % I[0, 2], "iyz_kgm2": "%.6e" % I[1, 2],
                      "mass_basis": "datasheet mass; inertia = STEP at uniform density scaled to that mass (estimate)"})
        else:
            d = {"part": e["id"], "name": e["name"], "file": "", "mass_basis": "datasheet or BOM mass (no STEP read)"}
        d.update({"status": "purchased", "qty_on_2_0": e["qty"], "bom": e["id"], "material": "purchased",
                  "material_source": "", "mass_kg": e["mass_kg"], "density_source": e["mass_source"],
                  "estimate": "yes" if e.get("estimate") else "no", "unit_check": ""})
        rows.append(d)
    with open(os.path.join(out, "part_massprops.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for d in rows:
            w.writerow({k: d.get(k, "") for k in cols})

    ccols = ["level", "id", "name", "ledger_kg", "cad_kg", "diff_kg", "diff_pct", "flag", "com_shift_mm", "cad_basis",
             "ledger_source", "note", "ledger_com_m", "cad_com_m", "ledger_inertia_diag", "cad_inertia"]
    with open(os.path.join(out, "link_comparison.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=ccols)
        w.writeheader()
        for d in res.get("comparison", []):
            w.writerow({k: (json.dumps(d[k]) if isinstance(d.get(k), list) else d.get(k, "")) for k in ccols})

    def item_json(it):
        return {"mass_kg": r(it["m"], 4), "com_m": [r(x, 5) for x in it["c"]], "inertia_kgm2": [[r(x, 6) for x in row] for row in it["I"]],
                "principal_kgm2": [r(x, 6) for x in principal(it["I"])[0]]}

    js = {"frame": res["frame"],
          "rollup": {k: {"parts": v["parts"], "instances": v["n"], "cad_assembly_frame": item_json(v["cad"]),
                         "base_footprint": item_json(v["base_footprint"]), "base_link": item_json(v["base_link"])}
                     for k, v in res["rollup"].items()},
          "placed": [{"part": pl["part"], "leaf": pl["leaf"], "volume_cm3": r(pl["p"]["vol"] * 1e6, 3),
                      "com_cad_mm": [r(x * 1000, 2) for x in pl["p"]["com"]], "volume_matches_part_file": pl.get("vol_matches_file"),
                      "placement_corrected_from_box_min_mm": [r(x * 1000, 2) for x in pl["corrected_from_lo"]] if pl["corrected_from_lo"] else None}
                     for pl in res["placed"]],
          "excluded_unknown_material": sorted({pl["part"] for pl in res["excluded"]}),
          "void_in_full_assembly": res["void"], "reexport": res["reexport"]}
    if "base_link_new" in res:
        js["base_link_substituted"] = item_json(res["base_link_new"])
    with open(os.path.join(out, "massprops.json"), "w", encoding="utf-8") as f:
        json.dump(js, f, indent=1)
    print("wrote", out)


if __name__ == "__main__":
    main()
