#!/usr/bin/env python3
"""BOM checks for manufacturing/bom/components-bom.md and mechanical-bom.md.

Checks, per file:
  table     every Markdown table row has the number of columns of its header
  quantity  cells of a quantity column (Qty, Quantity) and every "xN" / "Nx" multiplier in a
            table cell are positive integers
  price     no currency amounts or prices (currency symbols or codes next to a number, or the
            words price / cost next to a number)
  contact   no personal e-mail addresses (role addresses such as info@ or sales@ are allowed)
            and no telephone numbers
  links     every relative link resolves to a tracked file or folder (check_hw_repo.py)

Known findings are listed in tools/ci/bom-allow.txt as "<check> <path>::<found text> <issue URL>";
an allowed finding is reported as ALLOWED and does not fail the run. The check proves the files
are well formed; it does not prove the parts, quantities or sources are right. Exit 1 on any error.
"""
import argparse
import importlib.util
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("check_hw_repo", HERE / "check_hw_repo.py")
hw = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(hw)

DEFAULT_FILES = ["manufacturing/bom/components-bom.md", "manufacturing/bom/mechanical-bom.md"]
QTY_HEADERS = {"qty", "qty.", "quantity", "quantities"}
SEPARATOR = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)*\|?\s*$")
MULTIPLIER = re.compile(r"(?<![\w.])[x×](\S+?)(?=[\s,;)|]|$)|(?<![\w.])(\S+?)×(?=\s)")
INTEGER = re.compile(r"^[1-9][0-9]*$")
NUM = r"\d+(?:[.,]\d+)*"
CURRENCY = re.compile(
    rf"[$€£¥₹]\s?{NUM}|{NUM}\s?[$€£¥₹]|\b(?:USD|EUR|GBP|CNY|RMB|JPY|INR|CHF)\b\s?{NUM}"
    rf"|{NUM}\s?\b(?:USD|EUR|GBP|CNY|RMB|JPY|INR|CHF)\b|\b(?:prices?|unit cost|costs?)\b\W{{0,3}}{NUM}", re.I)
EMAIL = re.compile(r"\b([A-Za-z0-9._%+-]+)@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
ROLE_MAILBOX = re.compile(r"^(?:info|sales|support|contact|service|office|hello|noreply|no-reply|"
                          r"trade\d*|orders?|export|marketing|admin|enquir(?:y|ies)|help)$", re.I)
PHONE = re.compile(r"\+\d[\d\s().-]{7,}\d|\b(?:tel|phone|mobile|whatsapp|wechat)\b\W{0,3}[\d+][\d\s().-]{6,}\d", re.I)


def split_row(line):
    """Cells of a Markdown table row; ignores pipes escaped with a backslash or inside code spans."""
    text = re.sub(r"`[^`]*`", lambda m: m.group(0).replace("|", "\0"), line.strip())
    text = text.replace("\\|", "\0")
    if text.startswith("|"):
        text = text[1:]
    if text.endswith("|"):
        text = text[:-1]
    return [c.replace("\0", "|").strip() for c in text.split("|")]


def tables(text):
    """Yield (header_line_no, header_cells, [(line_no, cells), ...]) for each table."""
    lines = text.splitlines()
    i = 0
    while i < len(lines) - 1:
        if "|" in lines[i] and SEPARATOR.match(lines[i + 1]):
            header = split_row(lines[i])
            rows = []
            j = i + 2
            while j < len(lines) and lines[j].strip().startswith("|"):
                rows.append((j + 1, split_row(lines[j])))
                j += 1
            yield i + 1, header, rows
            i = j
        else:
            i += 1


def check_file(rel, text):
    findings = []  # (check, path, found, line, message)
    for header_no, header, rows in tables(text):
        qty_cols = [k for k, h in enumerate(header) if re.sub(r"[*_]", "", h).strip().lower() in QTY_HEADERS]
        for line_no, cells in rows:
            if len(cells) != len(header):
                findings.append(("table", rel, f"line {line_no}", line_no,
                                 f"row has {len(cells)} columns, header (line {header_no}) has {len(header)}"))
            for k in qty_cols:
                if k < len(cells) and not INTEGER.match(re.sub(r"[*_]", "", cells[k])):
                    findings.append(("quantity", rel, cells[k], line_no,
                                     f"quantity '{cells[k]}' in column '{header[k]}' is not a positive integer"))
            for cell in cells:
                for m in MULTIPLIER.finditer(cell):
                    value = re.sub(r"[*_]", "", m.group(1) or m.group(2))
                    # only numeric multipliers ("x2", "4x", "x0", "x1.5"); words such as "x-axis" are not
                    if re.match(r"^[-+]?\d", value) and not INTEGER.match(value):
                        findings.append(("quantity", rel, m.group(0), line_no,
                                         f"multiplier '{m.group(0)}' is not a positive integer"))
    for line_no, line in enumerate(text.splitlines(), 1):
        for m in CURRENCY.finditer(line):
            findings.append(("price", rel, m.group(0), line_no, f"currency amount or price '{m.group(0)}'"))
        for m in EMAIL.finditer(line):
            if not ROLE_MAILBOX.match(m.group(1)):
                findings.append(("contact", rel, m.group(0), line_no, f"personal e-mail address '{m.group(0)}'"))
        for m in PHONE.finditer(line):
            findings.append(("contact", rel, m.group(0).strip(), line_no, f"telephone number '{m.group(0).strip()}'"))
    return findings


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", default=".")
    parser.add_argument("--allow", default="tools/ci/bom-allow.txt")
    parser.add_argument("files", nargs="*", default=DEFAULT_FILES)
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    allowed = hw.load_allow(root / args.allow)
    tracked = hw.tracked(root)
    findings = []
    for rel in args.files:
        path = root / rel
        if not path.is_file():
            findings.append(("missing", rel, rel, 1, "BOM file not found"))
            continue
        findings += check_file(rel, path.read_text(encoding="utf-8"))
    link_findings = hw.check_links(root, tracked)
    for rel in args.files:
        findings += [(c, p, msg, 1, msg) for c, p, msg in link_findings if p == rel]
    failed = allowed_count = 0
    for check, rel, found, line, message in findings:
        key = (check, f"{rel}::{found}")
        if key in allowed:
            print(f"ALLOWED [{check}] {rel}:{line}: {message} (tracked in {allowed[key]})")
            allowed_count += 1
        else:
            print(f"::error file={rel},line={line}::[{check}] {message}")
            failed += 1
    print(f"Checked {len(args.files)} BOM files: {failed} errors, {allowed_count} allowed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
