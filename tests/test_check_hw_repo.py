"""Tests for tools/ci/check_hw_repo.py. Run: python3 -m unittest discover -s tests -v"""
import importlib.util
import io
import struct
import subprocess
import tempfile
import unittest
import zipfile
from contextlib import redirect_stdout
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "ci" / "check_hw_repo.py"
spec = importlib.util.spec_from_file_location("check_hw_repo", SCRIPT)
chk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(chk)


def binary_stl(triangles):
    return b"x" * 80 + struct.pack("<I", triangles) + b"\0" * (50 * triangles)


class Repo:
    def __init__(self, files, attributes="*.pdf binary\n*.zip binary\n*.stl binary\n*.STEP binary\n"):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        files = dict(files)
        files.setdefault(".gitattributes", attributes)
        for name, content in files.items():
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content if isinstance(content, bytes) else content.encode("utf-8"))
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        subprocess.run(["git", "-C", str(self.root), "add", "-A"], check=True)

    def run(self, allow=None):
        if allow is not None:
            (self.root / "tools" / "ci").mkdir(parents=True, exist_ok=True)
            (self.root / "tools" / "ci" / "hw-check-allow.txt").write_text(allow)
        out = io.StringIO()
        try:
            with redirect_stdout(out):
                code = chk.main(["--root", str(self.root)])
        finally:
            self.tmp.cleanup()
        return code, out.getvalue()


PDF = b"%PDF-1.7\n...\n%%EOF\n"


class Links(unittest.TestCase):
    def test_valid_file_and_folder_links_pass(self):
        code, out = Repo({"README.md": "[a](docs/a.md) [b](docs/) [w](https://example.com) [s](#top)",
                          "docs/a.md": "x"}).run()
        self.assertEqual(code, 0, out)

    def test_broken_link_fails(self):
        code, out = Repo({"README.md": "[a](docs/missing.md)"}).run()
        self.assertEqual(code, 1)
        self.assertIn("broken link: docs/missing.md", out)

    def test_link_text_path_must_match_target(self):
        # the 21 Oct regression: `TZBot/charger/` pointing to TZBot/
        code, out = Repo({"datasheets/README.md": "[`TZBot/charger/`](TZBot/)",
                          "datasheets/TZBot/charger/readme.md": "x"}).run()
        self.assertEqual(code, 1)
        self.assertIn("link text `TZBot/charger/` points to TZBot/", out)

    def test_basename_label_is_accepted(self):
        code, out = Repo({"README.md": "[`a.jpg`](img/a.jpg)", "img/a.jpg": b"\xff\xd8\xff\xe0"}).run()
        self.assertEqual(code, 0, out)

    def test_encoded_spaces_and_angle_brackets(self):
        code, out = Repo({"README.md": "[a](my%20file.pdf) [b](<my file.pdf>)", "my file.pdf": PDF}).run()
        self.assertEqual(code, 0, out)

    def test_links_in_code_blocks_are_ignored(self):
        code, out = Repo({"README.md": "```\n[a](nowhere.md)\n```\n"}).run()
        self.assertEqual(code, 0, out)


class Formats(unittest.TestCase):
    def test_valid_files_pass(self):
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as z:
            z.writestr("a.txt", "hello")
        code, out = Repo({"a.pdf": PDF, "m.STEP": "ISO-10303-21;\nHEADER;", "a.zip": buf.getvalue(),
                          "p.stl": binary_stl(3)}).run()
        self.assertEqual(code, 0, out)

    def test_html_saved_as_pdf_fails(self):
        code, out = Repo({"a.pdf": b"<!DOCTYPE html>"}).run()
        self.assertEqual(code, 1)
        self.assertIn("not a valid .pdf", out)

    def test_truncated_pdf_fails(self):
        code, out = Repo({"a.pdf": b"%PDF-1.7\nhalf a file"}).run()
        self.assertIn("no %%EOF", out)

    def test_split_zip_last_part_fails(self):
        # end-of-archive record claiming disk 1: the last part of a split archive
        eocd = b"PK\x05\x06" + struct.pack("<HHHHIIH", 1, 0, 0, 0, 0, 0, 0)
        code, out = Repo({"a.zip": b"\x96\xd5\xd4\x3d" + b"\0" * 100 + eocd}).run()
        self.assertEqual(code, 1)
        self.assertIn("split ZIP archive", out)

    def test_truncated_stl_fails(self):
        code, out = Repo({"p.stl": binary_stl(3)[:-10]}).run()
        self.assertIn("does not match 3 triangles", out)

    def test_lfs_pointer_fails(self):
        code, out = Repo({"m.STEP": "version https://git-lfs.github.com/spec/v1\noid sha256:abc\n"}).run()
        self.assertIn("Git LFS pointer", out)


class Attributes(unittest.TestCase):
    def test_cad_file_without_binary_attribute_fails(self):
        code, out = Repo({"m.STEP": "ISO-10303-21;"}, attributes="*.pdf binary\n").run()
        self.assertEqual(code, 1)
        self.assertIn("not marked binary", out)


class Datasheets(unittest.TestCase):
    def test_unindexed_vendor_folder_fails(self):
        code, out = Repo({"datasheets/README.md": "[`ACME/`](ACME/)", "datasheets/ACME/a.pdf": PDF,
                          "datasheets/Other/b.pdf": PDF}).run()
        self.assertEqual(code, 1)
        self.assertIn("datasheets/Other/", out)


class Allow(unittest.TestCase):
    def test_allowed_finding_does_not_fail(self):
        code, out = Repo({"a.pdf": b"junk"}).run(
            allow="format a.pdf https://github.com/openAMRobot/openamr-platform-hw/issues/1\n")
        self.assertEqual(code, 0, out)
        self.assertIn("ALLOWED", out)

    def test_allow_entry_needs_issue_url(self):
        with self.assertRaises(SystemExit):
            Repo({"a.pdf": b"junk"}).run(allow="format a.pdf later\n")


if __name__ == "__main__":
    unittest.main()
