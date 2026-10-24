"""Tests for tools/ci/check_bom.py. Run: python3 -m unittest discover -s tests -v

Fixtures live in tests/fixtures/bom/*.md.in (not .md, so the repository link check does not
scan the deliberately broken ones); each test copies them into a temporary git repository.
"""
import importlib.util
import io
import shutil
import subprocess
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "ci" / "check_bom.py"
FIXTURES = ROOT / "tests" / "fixtures" / "bom"
spec = importlib.util.spec_from_file_location("check_bom", SCRIPT)
chk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(chk)


def run(names, allow=None):
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        bom = root / "bom"
        bom.mkdir()
        for f in FIXTURES.glob("*.md.in"):
            shutil.copy(f, bom / f.name[:-3])
        if allow is not None:
            (root / "allow.txt").write_text(allow, encoding="utf-8")
        subprocess.run(["git", "init", "-q", str(root)], check=True)
        subprocess.run(["git", "-C", str(root), "add", "-A"], check=True)
        out = io.StringIO()
        with redirect_stdout(out):
            code = chk.main(["--root", str(root), "--allow", "allow.txt", *[f"bom/{n}" for n in names]])
        return code, out.getvalue()


class Valid(unittest.TestCase):
    def test_valid_fixture_passes(self):
        code, out = run(["valid.md"])
        self.assertEqual(code, 0, out)
        self.assertIn("0 errors", out)


class Table(unittest.TestCase):
    def test_row_with_extra_column_fails(self):
        code, out = run(["bad-table.md"])
        self.assertEqual(code, 1)
        self.assertIn("[table] row has 3 columns, header (line 1) has 2", out)


class Quantity(unittest.TestCase):
    def test_range_and_zero_quantities_fail(self):
        code, out = run(["bad-qty.md"])
        self.assertEqual(code, 1)
        self.assertIn("quantity '1–2' in column 'Qty'", out)
        self.assertIn("quantity '0' in column 'Qty'", out)

    def test_fractional_and_zero_multipliers_fail(self):
        code, out = run(["bad-multiplier.md"])
        self.assertEqual(code, 1)
        self.assertIn("multiplier '×1.5'", out)
        self.assertIn("multiplier 'x0'", out)

    def test_allowed_finding_does_not_fail(self):
        code, out = run(["bad-qty.md"], allow=(
            "quantity bom/bad-qty.md::1–2 https://github.com/openAMRobot/openamr-platform-hw/issues/36\n"
            "quantity bom/bad-qty.md::0 https://github.com/openAMRobot/openamr-platform-hw/issues/36\n"))
        self.assertEqual(code, 0, out)
        self.assertIn("2 allowed", out)

    def test_allow_entry_without_issue_is_rejected(self):
        with self.assertRaises(SystemExit):
            run(["bad-qty.md"], allow="quantity bom/bad-qty.md::0 none\n")


class Price(unittest.TestCase):
    def test_prices_and_currency_amounts_fail(self):
        code, out = run(["bad-price.md"])
        self.assertEqual(code, 1)
        self.assertIn("'price: 12'", out)
        self.assertIn("'€45.00'", out)
        self.assertIn("'30 USD'", out)


class Contact(unittest.TestCase):
    def test_personal_email_and_phones_fail(self):
        code, out = run(["bad-contact.md"])
        self.assertEqual(code, 1)
        self.assertIn("personal e-mail address 'jane.doe@example.com'", out)
        self.assertIn("telephone number 'mobile +86 138 0013 8000'", out)
        self.assertIn("telephone number 'WeChat: 13800138000'", out)

    def test_role_address_passes(self):
        self.assertEqual(chk.check_file("x.md", "write to sales@example.com or trade26@example.com"), [])


class Links(unittest.TestCase):
    def test_broken_relative_link_fails(self):
        code, out = run(["bad-link.md"])
        self.assertEqual(code, 1)
        self.assertIn("[links] broken link: no-such-file.md", out)


class RepositoryBoms(unittest.TestCase):
    def test_checked_in_boms_pass_with_the_allow_list(self):
        out = io.StringIO()
        with redirect_stdout(out):
            code = chk.main(["--root", str(ROOT)])
        self.assertEqual(code, 0, out.getvalue())


if __name__ == "__main__":
    unittest.main()
