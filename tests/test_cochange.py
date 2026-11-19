"""Deterministic checks for cochange.sh on a small generated history. Run: python3 -m unittest discover tests"""
import os
import shutil
import subprocess
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COCHANGE = os.path.join(ROOT, "skills", "audit", "scripts", "cochange.sh")


class CochangeTest(unittest.TestCase):
    def history(self, files, commits=3):
        """A repo where every listed file changes in each of `commits` commits."""
        repo = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, repo)
        git = lambda *a: subprocess.run(["git", "-C", repo, "-c", "user.email=t@t", "-c", "user.name=t", *a],
                                        check=True, capture_output=True)
        git("init", "-q")
        for n in range(commits):
            for path in files:
                os.makedirs(os.path.dirname(os.path.join(repo, path)) or repo, exist_ok=True)
                with open(os.path.join(repo, path), "a", encoding="utf-8") as f:
                    f.write(f"{n}\n")
            git("add", "-A"); git("commit", "-qm", f"change {n}")
        return repo

    def pairs(self, repo, *args):
        out = subprocess.run(["sh", COCHANGE, *args], cwd=repo, capture_output=True, text=True, check=True).stdout
        return [tuple(line.split("\t")) for line in out.splitlines()]

    def test_lists_cross_folder_pairs_and_skips_same_folder_pairs_and_lockfiles(self):
        repo = self.history(["api/order.ts", "api/status.ts", "ui/badge.ts", "package-lock.json"])
        self.assertEqual(self.pairs(repo), [("3", "100%", "api/order.ts", "ui/badge.ts"),
                                            ("3", "100%", "api/status.ts", "ui/badge.ts")])

    def test_pairs_below_the_minimum_are_dropped(self):
        repo = self.history(["api/order.ts", "ui/badge.ts"], commits=2)
        self.assertEqual(self.pairs(repo), [])
        self.assertEqual(self.pairs(repo, "12 months ago", "2"), [("2", "100%", "api/order.ts", "ui/badge.ts")])

    def test_non_ascii_names_are_not_quoted_into_a_folder_of_their_own(self):
        repo = self.history(["api/commande-reçue.ts", "api/status.ts"])
        self.assertEqual(self.pairs(repo), [])  # same folder, so no pair

    def test_exclude_drops_matching_paths(self):
        repo = self.history(["api/order.ts", "ui/badge.ts", "notes/log.md"])
        env = dict(os.environ, EXCLUDE="^notes/")
        out = subprocess.run(["sh", COCHANGE], cwd=repo, capture_output=True, text=True, check=True, env=env).stdout
        self.assertEqual(out, "3\t100%\tapi/order.ts\tui/badge.ts\n")


if __name__ == "__main__":
    unittest.main()
