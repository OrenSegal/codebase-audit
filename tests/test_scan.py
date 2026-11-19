"""Deterministic checks for scan.py routing. Run: python3 -m unittest discover tests"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import unittest.mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCAN = os.path.join(ROOT, "skills", "audit", "scripts", "scan.py")
FIXTURE = os.path.join(ROOT, "evals", "seeded-bugs", "fixtures", "pantry")


def scan(*args):
    return subprocess.run([sys.executable, SCAN, *args], capture_output=True, text=True, check=True).stdout


class ManifestTest(unittest.TestCase):
    def test_manifests_share_one_version(self):
        def load(*path):
            with open(os.path.join(ROOT, *path)) as f:
                return json.load(f)
        version = load(".claude-plugin", "plugin.json")["version"]  # the one home; the others copy it
        self.assertEqual(load(".claude-plugin", "marketplace.json")["plugins"][0]["version"], version)
        self.assertEqual(load("gemini-extension.json")["version"], version)


class ScanTest(unittest.TestCase):
    def setUp(self):
        self.repo = tempfile.mkdtemp()
        shutil.copytree(FIXTURE, self.repo, dirs_exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.repo)

    def test_signals_and_lenses_agree(self):
        self.assertTrue(scan("--check").startswith("ok:"))

    def test_readme_lens_table_matches_lens_files(self):
        sys.path.insert(0, os.path.dirname(SCAN))
        from scan import load_lenses, read_text
        readme = read_text(os.path.join(ROOT, "README.md")).splitlines()
        for name, lens in load_lenses().items():
            row = next(r for r in readme if r.startswith(f"| {name} |")).split("|")
            listed = [{p.strip() for p in cell.split(",")} - {"none"} for cell in (row[3], row[4])]
            self.assertEqual(listed[0], set(lens.probes) - lens.conditional, f"{name} unconditional probes")
            self.assertEqual(listed[1], set(lens.conditional), f"{name} conditional probes")

    def test_readme_fundamentals_match_skill(self):
        sys.path.insert(0, os.path.dirname(SCAN))
        from scan import load_fundamentals
        skill = load_fundamentals()
        self.assertEqual(len(skill), 14)
        self.assertEqual(load_fundamentals(os.path.join(ROOT, "README.md")), skill)

    def test_readme_counts_match_the_lens_files(self):
        sys.path.insert(0, os.path.dirname(SCAN))
        from scan import ALWAYS, load_lenses, read_text
        readme, lenses = read_text(os.path.join(ROOT, "README.md")), load_lenses()
        words = {8: "eight", 6: "six", 14: "fourteen"}
        self.assertIn(f"{sum(len(l.probes) for l in lenses.values())} probes in {len(lenses)} lenses", readme)
        self.assertIn(f"{words[len(ALWAYS)]} lenses always run, {words[len(lenses) - len(ALWAYS)]} more fire", readme)

    def test_check_reports_unmapped_and_unknown_probes(self):
        sys.path.insert(0, os.path.dirname(SCAN))
        import contextlib
        import io
        import scan as scan_module
        real = scan_module.load_fundamentals()
        broken = dict(real, F1=(real["F1"][0], real["F1"][1][1:] + ("types.no-such-probe", "design.copies")))
        out = io.StringIO()
        with unittest.mock.patch.object(scan_module, "load_fundamentals", return_value=broken), \
                contextlib.redirect_stdout(out):
            scan_module.cmd_check(scan_module.argparse.Namespace(root=ROOT))
        text = out.getvalue()
        self.assertIn(f"probe {real['F1'][1][0]} tests no fundamental", text)
        self.assertIn("F1: names types.no-such-probe, which no lens file has", text)
        self.assertIn("probe design.copies is under 2 fundamentals", text)

    def test_routes_lenses_from_project_signals(self):
        out = scan(self.repo)
        for lens in ("money", "data", "ux", "evolution", "types", "failure"):
            self.assertIn(f"- **{lens}** fires", out)
        self.assertIn("- ai skipped", out)
        self.assertIn("plan: sequential", out)

    def test_seeds_point_at_planted_defects(self):
        out = scan(self.repo)
        for site in ("src/items/sync.ts", "src/items/status.ts", "001_items.sql", "src/scan/quota.ts"):
            self.assertIn(site, out)

    def test_special_counts(self):
        counts = dict(line.split() for line in scan(self.repo, "--special").splitlines())
        self.assertGreaterEqual(int(counts["swallowed-errors"]), 1)
        self.assertGreaterEqual(int(counts["catch-alls"]), 1)

    def test_project_local_signals_fire_a_lens(self):
        local = os.path.join(self.repo, "docs", "agents")
        os.makedirs(local)
        with open(os.path.join(local, "audit-signals.tsv"), "w") as f:
            f.write("signal\thouse-ai\tai\tcode\twatchItems\t-\n")
        self.assertIn("- **ai** fires: house-ai", scan(self.repo))


if __name__ == "__main__":
    unittest.main()
