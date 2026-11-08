"""Deterministic checks for verify.py. Run: python3 -m unittest discover tests"""
import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERIFY = os.path.join(ROOT, "skills", "audit", "scripts", "verify.py")
REPO = os.path.join(ROOT, "evals", "seeded-bugs", "fixtures", "pantry")

FINDING = """### MONEY-1 Scan counter lives in localStorage
- where: src/scan/quota.ts:13
- probe: counter-integrity
- scenario: user clears site data → scansLeft resets to 5
- severity: high
- detectability: silent
- verdict: CONFIRMED (repro/quota.test.js)
- fix family: server-side atomic counter
"""
CLEAN = """clean: truth-table — one plan, checked in quota.ts
clean: entitlement-source — covered by MONEY-1's fix family
clean: store-webhooks — n/a: no webhook route in this slice
clean: money-arithmetic — no prices handled
clean: paywall-honesty — no paywall copy
"""


def run(findings, report=None):
    out = tempfile.mkdtemp()
    os.makedirs(os.path.join(out, "findings"))
    with open(os.path.join(out, "findings", "money.md"), "w") as f:
        f.write(findings)
    if report is not None:
        with open(os.path.join(out, "REPORT.md"), "w") as f:
            f.write(report)
    r = subprocess.run([sys.executable, VERIFY, out, "--root", REPO], capture_output=True, text=True)
    return r.returncode, r.stdout


class VerifyTest(unittest.TestCase):
    def test_complete_findings_verify(self):
        code, out = run(FINDING + CLEAN, report="- fix [local, high]\n  - MONEY-1")
        self.assertEqual(code, 0, out)
        self.assertIn("verified: 1 findings (1 high)", out)

    def test_unanswered_probe_fails(self):
        code, out = run(FINDING + CLEAN.replace("clean: paywall-honesty — no paywall copy\n", ""))
        self.assertEqual(code, 1)
        self.assertIn("probe 'paywall-honesty' has no finding and no clean line", out)

    def test_na_cannot_close_an_unconditional_probe(self):
        code, out = run(FINDING + CLEAN.replace("money-arithmetic — no prices handled", "money-arithmetic — n/a: none"))
        self.assertEqual(code, 1)
        self.assertIn("'money-arithmetic' is unconditional", out)

    def test_missing_field_bad_path_and_unreproduced_confirmed_fail(self):
        broken = (FINDING.replace("- detectability: silent\n", "")
                  .replace("src/scan/quota.ts:13", "src/nope.ts:1")
                  .replace("CONFIRMED (repro/quota.test.js)", "CONFIRMED"))
        code, out = run(broken + CLEAN)
        self.assertEqual(code, 1)
        for problem in ("missing field 'detectability'", "where path 'src/nope.ts' does not exist",
                        "CONFIRMED verdict names no reproduction"):
            self.assertIn(problem, out)

    def test_report_must_place_every_finding(self):
        code, out = run(FINDING + CLEAN, report="nothing here")
        self.assertEqual(code, 1)
        self.assertIn("REPORT.md does not place MONEY-1", out)


if __name__ == "__main__":
    unittest.main()
