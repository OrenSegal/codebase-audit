"""Every eval case's scaffold builds its workspace from a clean clone. No model is called.
Run: python3 -m unittest discover tests"""
import glob
import os
import subprocess
import tempfile
import unittest

EVALS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "evals")


def scaffold(case):
    work = tempfile.mkdtemp()
    r = subprocess.run(["bash", os.path.join(EVALS, case, "scaffold.sh")], cwd=work, capture_output=True, text=True)
    return work, r


class ScaffoldTest(unittest.TestCase):
    def test_every_scaffold_succeeds(self):
        cases = sorted(os.path.basename(os.path.dirname(p)) for p in glob.glob(os.path.join(EVALS, "*", "scaffold.sh")))
        self.assertEqual(len(cases), 5)
        for case in cases:
            with self.subTest(case=case):
                _, r = scaffold(case)
                self.assertEqual(r.returncode, 0, r.stderr)

    def test_work_the_map_starts_from_a_finished_audit_with_approval(self):
        work, _ = scaffold("work-the-map")
        for path in (".audit/HANDOFF.md", ".audit/REPORT.md", ".audit/repro/webhook.test.js"):
            self.assertTrue(os.path.isfile(os.path.join(work, path)), path)
        with open(os.path.join(work, ".audit", "HANDOFF.md")) as f:
            self.assertIn("- approved: 01, 02", f.read())

    def test_resume_unapproved_has_the_hand_off_without_approval(self):
        work, _ = scaffold("resume-unapproved")
        with open(os.path.join(work, ".audit", "HANDOFF.md")) as f:
            text = f.read()
        self.assertIn("- next:", text)
        self.assertNotIn("- approved:", text)


if __name__ == "__main__":
    unittest.main()
