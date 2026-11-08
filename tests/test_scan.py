"""Deterministic checks for scan.py routing. Run: python3 -m unittest discover tests"""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCAN = os.path.join(ROOT, "skills", "audit", "scripts", "scan.py")
FIXTURE = os.path.join(ROOT, "evals", "seeded-bugs", "fixtures", "pantry")


def scan(*args):
    return subprocess.run([sys.executable, SCAN, *args], capture_output=True, text=True, check=True).stdout


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
