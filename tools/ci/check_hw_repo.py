#!/usr/bin/env python3
"""Repository checks for openamr-platform-hw.

Checks every tracked file (git ls-files) for:
  links       relative Markdown links and images point to a tracked file or folder
  format      binary engineering files start with their format signature and are complete
              (PDF, STEP, ZIP/XLSX incl. split-archive detection, PNG, JPEG, DWG, STL)
  lfs         no Git LFS pointer files (LFS is not used in this repository)
  size        no file above 95 MiB (GitHub rejects 100 MiB); warning above 50 MiB
  attributes  CAD, PDF and archive files are marked binary in .gitattributes
  datasheets  every vendor folder under datasheets/ is linked from datasheets/README.md

Known findings are listed in tools/ci/hw-check-allow.txt as "<check> <path> <issue URL>".
An allowed finding is reported as ALLOWED and does not fail the run. Exit code 1 on any error.
"""
import argparse
import os
import re
import struct
import subprocess
import sys
import urllib.parse
import zipfile
from pathlib import Path

MIB = 1024 * 1024
FAIL_BYTES = 95 * MIB
WARN_BYTES = 50 * MIB
BINARY_EXT = {"pdf", "step", "stp", "sldprt", "sldasm", "slddrw", "dxf", "dwg", "stl", "zip", "xlsx", "3mf"}
LINK = re.compile(r"!?\[([^\]]*)\]\(\s*(<[^>]+>|[^)\s]+)(?:\s+\"[^\"]*\")?\s*\)")
CODE_PATH = re.compile(r"^`([^`\s]+/?)`$")
SIGNATURES = {
    "pdf": (b"%PDF-",),
    "step": (b"ISO-10303-21",), "stp": (b"ISO-10303-21",),
    "png": (b"\x89PNG\r\n\x1a\n",),
    "jpg": (b"\xff\xd8\xff",), "jpeg": (b"\xff\xd8\xff",),
    "dwg": (b"AC10",),
}


def tracked(root):
    out = subprocess.check_output(["git", "-C", str(root), "ls-files", "-z"])
    return [p for p in out.decode("utf-8").split("\0") if p]


def check_links(root, files):
    findings = []
    paths = set(files)
    dirs = {str(Path(p).parent) for p in files} | {"."}
    for d in list(dirs):
        parts = Path(d).parts
        for i in range(1, len(parts)):
            dirs.add(str(Path(*parts[:i])))
    for f in files:
        if not f.lower().endswith(".md"):
            continue
        text = (root / f).read_text(encoding="utf-8", errors="replace")
        text = re.sub(r"```.*?```", "", text, flags=re.S)
        for m in LINK.finditer(text):
            label, target = m.group(1).strip(), m.group(2).strip("<>")
            if re.match(r"^[a-z][a-z0-9+.-]*:", target, re.I) or target.startswith("#"):
                continue
            target = urllib.parse.unquote(target.split("#", 1)[0].split("?", 1)[0])
            if not target:
                continue
            base = Path(f).parent
            resolved = os.path.normpath(str(base / target)) if not target.startswith("/") else target.lstrip("/")
            resolved = resolved.rstrip("/") or "."
            if resolved.startswith(".."):
                findings.append(("links", f, f"link leaves the repository: {target}"))
            elif resolved not in paths and resolved not in dirs:
                findings.append(("links", f, f"broken link: {target}"))
            else:
                named = CODE_PATH.match(label)
                if named and not re.match(r"^[a-z][a-z0-9+.-]*:", named.group(1), re.I):
                    name = named.group(1).rstrip("/")
                    want = os.path.normpath(str(base / name)) if "/" in name else None
                    if (want != resolved) if want else (Path(resolved).name != name):
                        findings.append(("links", f, f"link text `{named.group(1)}` points to {target}"))
    return findings


def zip_problem(path):
    with open(path, "rb") as fh:
        data = fh.read()
    if not data.startswith(b"PK\x03\x04") and not data.startswith(b"PK\x05\x06"):
        eocd = data.rfind(b"PK\x05\x06")
        if eocd >= 0 and struct.unpack("<H", data[eocd + 4:eocd + 6])[0] > 0:
            return "split ZIP archive (last part only); the earlier parts are missing"
        return "not a ZIP file (missing PK signature)"
    eocd = data.rfind(b"PK\x05\x06")
    if eocd < 0:
        return "ZIP end-of-archive record missing (truncated file)"
    if struct.unpack("<H", data[eocd + 4:eocd + 6])[0] > 0:
        return "split ZIP archive; the other parts are missing"
    try:
        with zipfile.ZipFile(path) as z:
            for info in z.infolist():
                with z.open(info) as member:
                    while member.read(1 << 20):
                        pass
    except zipfile.BadZipFile as exc:
        if "File name in directory" in str(exc):
            return None  # non-UTF-8 entry names; content still checked by CRC elsewhere
        return f"corrupt ZIP: {exc}"
    except Exception as exc:  # zlib or CRC errors
        return f"corrupt ZIP: {exc}"
    return None


def stl_problem(path):
    data = path.read_bytes()
    if data[:5].lower() == b"solid" and b"facet" in data[:4096]:
        return None if b"endsolid" in data[-512:].lower() else "ASCII STL without endsolid (truncated)"
    if len(data) < 84:
        return "STL shorter than its 84-byte header"
    count = struct.unpack("<I", data[80:84])[0]
    if len(data) != 84 + 50 * count:
        return f"binary STL size {len(data)} does not match {count} triangles (truncated or corrupt)"
    return None


def check_formats(root, files):
    findings = []
    for f in files:
        ext = f.rsplit(".", 1)[-1].lower() if "." in Path(f).name else ""
        path = root / f
        with open(path, "rb") as fh:
            head = fh.read(200)
        if head.startswith(b"version https://git-lfs.github.com/spec/"):
            findings.append(("lfs", f, "Git LFS pointer committed instead of the file"))
            continue
        if ext in SIGNATURES and not any(head.startswith(s) for s in SIGNATURES[ext]):
            findings.append(("format", f, f"not a valid .{ext} file (signature {head[:8]!r})"))
        elif ext in {"zip", "xlsx"}:
            problem = zip_problem(path)
            if problem:
                findings.append(("format", f, problem))
        elif ext == "stl":
            problem = stl_problem(path)
            if problem:
                findings.append(("format", f, problem))
        if ext == "pdf" and b"%%EOF" not in path.read_bytes()[-2048:]:
            findings.append(("format", f, "PDF has no %%EOF marker at the end (truncated)"))
    return findings


def check_sizes(root, files):
    errors, warnings = [], []
    for f in files:
        size = (root / f).stat().st_size
        if size > FAIL_BYTES:
            errors.append(("size", f, f"{size / MIB:.1f} MiB exceeds 95 MiB; GitHub rejects files of 100 MiB"))
        elif size > WARN_BYTES:
            warnings.append(("size", f, f"{size / MIB:.1f} MiB is above 50 MiB"))
    return errors, warnings


def check_attributes(root, files):
    candidates = [f for f in files if "." in Path(f).name and f.rsplit(".", 1)[-1].lower() in BINARY_EXT]
    if not candidates:
        return []
    out = subprocess.run(["git", "-C", str(root), "check-attr", "-z", "binary", "--stdin"],
                         input="\0".join(candidates).encode("utf-8") + b"\0",
                         capture_output=True, check=True).stdout.decode("utf-8").split("\0")
    findings = []
    for i in range(0, len(out) - 2, 3):
        path, _, value = out[i], out[i + 1], out[i + 2]
        if value != "set":
            findings.append(("attributes", path, "not marked binary in .gitattributes"))
    return findings


def check_datasheets(root, files):
    readme = root / "datasheets" / "README.md"
    if not readme.is_file():
        return []
    text = readme.read_text(encoding="utf-8")
    targets = {urllib.parse.unquote(m.group(2).strip("<>")).split("/")[0] for m in LINK.finditer(text)}
    vendors = sorted({Path(f).parts[1] for f in files
                      if f.startswith("datasheets/") and len(Path(f).parts) > 2})
    return [("datasheets", f"datasheets/{v}/", "vendor folder not linked from datasheets/README.md")
            for v in vendors if v not in targets]


def load_allow(path):
    allowed = {}
    if path.is_file():
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            check, rest = line.split(None, 1)
            target, issue = rest.rsplit(None, 1)
            if not issue.startswith("https://github.com/"):
                raise SystemExit(f"allow entry needs a tracking issue URL: {line}")
            allowed[(check, target)] = issue
    return allowed


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", default=".")
    parser.add_argument("--allow", default="tools/ci/hw-check-allow.txt")
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    files = tracked(root)
    allowed = load_allow(root / args.allow)
    errors = []
    errors += check_links(root, files)
    errors += check_formats(root, files)
    size_errors, warnings = check_sizes(root, files)
    errors += size_errors
    errors += check_attributes(root, files)
    errors += check_datasheets(root, files)
    failed = 0
    for check, path, message in warnings:
        print(f"::warning file={path}::[{check}] {message}")
    for check, path, message in errors:
        if (check, path) in allowed:
            print(f"ALLOWED [{check}] {path}: {message} (tracked in {allowed[(check, path)]})")
        else:
            print(f"::error file={path}::[{check}] {message}")
            failed += 1
    print(f"Checked {len(files)} files: {failed} errors, {len(warnings)} warnings, "
          f"{sum(1 for c, p, _ in errors if (c, p) in allowed)} allowed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
