"""Deterministic checks for scan.py routing. Run: python3 -m unittest discover tests"""
import json
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


    def local_signals(self, text):
        local = os.path.join(self.repo, "docs", "agents")
        os.makedirs(local)
        with open(os.path.join(local, "audit-signals.tsv"), "w") as f:
            f.write(text)
        return subprocess.run([sys.executable, SCAN, self.repo], capture_output=True, text=True)

    def test_unknown_row_type_is_refused_with_file_and_line(self):
        r = self.local_signals("# house rows\nsede\ttypes.catch-all\t-\tcode\twatchItems\t-\n")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("audit-signals.tsv:2: unknown row type 'sede'", r.stderr)
        self.assertEqual(r.stdout, "")


    def test_wrong_column_count_is_refused_with_file_and_line(self):
        r = self.local_signals("seed\ttypes.catch-all\tcode\twatchItems\t-\n")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("audit-signals.tsv:1: expected 6 tab-separated columns, got 5", r.stderr)

    def test_bad_regex_is_refused_with_file_and_line(self):
        r = self.local_signals("seed\ttypes.catch-all\t-\tcode\twatch(Items\t-\n")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("audit-signals.tsv:1: bad regex for types.catch-all", r.stderr)
        self.assertNotIn("Traceback", r.stderr)

    def test_check_names_a_seed_with_no_probe_and_a_signal_with_no_lens(self):
        self.local_signals("seed\ttypes.no-such-probe\t-\tcode\twatchItems\t-\n"
                           "signal\thouse\tno-such-lens\tcode\twatchItems\t-\n")
        r = subprocess.run([sys.executable, SCAN, self.repo, "--check"], capture_output=True, text=True)
        self.assertEqual(r.returncode, 1)
        self.assertIn("audit-signals.tsv:1: seed types.no-such-probe names no probe in lenses/types.md", r.stdout)
        self.assertIn("audit-signals.tsv:2: lens 'no-such-lens' has no lenses/no-such-lens.md", r.stdout)


if __name__ == "__main__":
    unittest.main()
