"""Deterministic checks for scan.py's planning, routing and diff mode. Run: python3 -m unittest discover tests"""
import collections
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "skills", "audit", "scripts"))
import scan  # noqa: E402

SCAN = os.path.join(ROOT, "skills", "audit", "scripts", "scan.py")


def write(path, text):
    with open(path, "w") as f:
        f.write(text)


def hits(**probe_counts):
    return collections.Counter({k.replace("__", "."): v for k, v in probe_counts.items()})


class PlanTest(unittest.TestCase):
    def test_small_scope_runs_sequentially(self):
        self.assertTrue(scan.plan(["types"], {}, {}, [], scan.SEQUENTIAL_MAX_FILES, 12).startswith("sequential"))

    def test_large_single_package_gets_one_subagent_per_lens(self):
        text = scan.plan(["types", "state"], {"types": 9}, {}, [], 500, 12)
        self.assertEqual(text, "parallel: 2 subagents (budget 12), one per lens")

    def test_spare_budget_shards_the_heaviest_lens_by_package(self):
        per_file = {"app/a.ts": hits(types__catch_all=60), "api/b.ts": hits(types__catch_all=40),
                    "app/c.ts": hits(state__lifetime=5)}
        load = {"types": 100, "state": 5}
        text = scan.plan(["types", "state"], load, per_file, ["api", "app"], 500, 3)
        self.assertIn("3 subagents (budget 3)", text)
        self.assertIn("shard types into app, api", text)
        self.assertNotIn("shard state", text)

    def test_shards_stay_within_budget(self):
        per_file = {f"p{i}/x.ts": hits(types__catch_all=10) for i in range(4)}
        text = scan.plan(["types", "state", "failure"], {"types": 40}, per_file, [f"p{i}" for i in range(4)], 500, 3)
        self.assertIn("3 subagents (budget 3)", text)
        self.assertNotIn("shard", text)

    def test_more_lenses_than_budget_run_in_waves(self):
        text = scan.plan(["types", "state", "failure"], {}, {}, [], 500, 2)
        self.assertEqual(text, "parallel in waves: 3 lenses, at most 2 subagents at once, heaviest lenses first")

    def test_small_packages_fold_into_rest(self):
        per_file = {"big/a.ts": hits(types__catch_all=90), "tiny/b.ts": hits(types__catch_all=5),
                    "tiny2/c.ts": hits(types__catch_all=5)}
        text = scan.plan(["types"], {"types": 100}, per_file, ["big", "tiny", "tiny2"], 500, 4)
        self.assertIn("shard types into big, rest", text)


class ToolsTest(unittest.TestCase):
    def setUp(self):
        self.repo = tempfile.mkdtemp()
        for path in ("web/tsconfig.json", "web/nested/tsconfig.json", "api/tsconfig.json", "web/node_modules/.bin/tsc", "a.py"):
            os.makedirs(os.path.dirname(os.path.join(self.repo, path)) or self.repo, exist_ok=True)
            write(os.path.join(self.repo, path), "")

    def tearDown(self):
        shutil.rmtree(self.repo)

    def runs(self, fired):
        files = ["web/tsconfig.json", "web/nested/tsconfig.json", "api/tsconfig.json", "a.py"]
        return [(t.name, folder, ok) for t, folder, ok in scan.relevant_tools(self.repo, files, fired)]

    def test_package_tools_run_once_per_outermost_package_and_check_local_bins(self):
        tsc = [r for r in self.runs({"types"}) if r[0] == "tsc"]
        self.assertEqual(tsc, [("tsc", "api", False), ("tsc", "web", True)])

    def test_root_tools_run_once_and_only_for_fired_lenses(self):
        self.assertIn(("vulture", ".", scan.shutil.which("vulture") is not None), self.runs({"design"}))
        self.assertNotIn("vulture", [r[0] for r in self.runs({"types"})])

    def test_every_tool_row_parses(self):
        tools = scan.load_tools()
        self.assertTrue(tools)
        self.assertTrue(all(t.runs_in in ("root", "package") for t in tools))


class RouteTest(unittest.TestCase):
    def test_requested_lenses_override_detection(self):
        fired, _ = scan.route([], {}, ["money"])
        self.assertEqual(fired, ["money"])

    def test_unknown_lens_is_refused(self):
        with self.assertRaises(SystemExit):
            scan.route([], {}, ["nope"])

    def test_always_lenses_fire_with_no_signals(self):
        fired, reasons = scan.route([], {}, None)
        self.assertEqual(set(fired), set(scan.ALWAYS))
        self.assertEqual(reasons["design"], ["always"])


class DiffModeTest(unittest.TestCase):
    def test_since_seeds_only_changed_files(self):
        repo = tempfile.mkdtemp()
        try:
            git = lambda *a: subprocess.run(["git", "-C", repo, "-c", "user.email=t@t", "-c", "user.name=t", *a],
                                            check=True, capture_output=True)
            git("init", "-q")
            write(os.path.join(repo, "old.ts"), "try { x() } catch {}\n")
            git("add", "-A"); git("commit", "-qm", "one")
            write(os.path.join(repo, "new.ts"), "try { y() } catch {}\n")
            git("add", "-A"); git("commit", "-qm", "two")
            out = subprocess.run([sys.executable, SCAN, repo, "--since", "HEAD~1"], capture_output=True, text=True).stdout
            self.assertIn("new.ts:1", out)
            self.assertNotIn("old.ts:1", out)
            self.assertIn("1 source files in scope", out)
        finally:
            shutil.rmtree(repo)


if __name__ == "__main__":
    unittest.main()
