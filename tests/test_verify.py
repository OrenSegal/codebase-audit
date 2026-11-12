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


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(text)


def verify(out, root=REPO):
    r = subprocess.run([sys.executable, VERIFY, out, "--root", root], capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def run(findings, report=None, refuted="none\n", scan="- **money** fires: requested\n", root=REPO):
    """Verify an output directory holding one money findings file plus the given companions (None leaves one out)."""
    out = tempfile.mkdtemp()
    write(os.path.join(out, "findings", "money.md"), findings)
    write(os.path.join(out, "repro", "quota.test.js"), "// red\n")
    for name, text in (("REPORT.md", report), ("refuted.md", refuted), ("SCAN.md", scan)):
        if text is not None:
            write(os.path.join(out, name), text)
    return verify(out, root)


def garbage_audit():
    """An output directory in the right shape with nothing true in it: every probe of every lens closed
    with a one-letter clean line, a finding outside the repo with an empty reproduction, a finding whose
    heading does not parse, and a report that names only the id LOL-10."""
    sys.path.insert(0, os.path.dirname(VERIFY))
    from scan import load_lenses
    out = tempfile.mkdtemp()
    lenses = load_lenses()
    for name, lens in lenses.items():
        write(os.path.join(out, "findings", name + ".md"), "".join(f"clean: {p} - x\n" for p in lens.probes))
    with open(os.path.join(out, "findings", "security.md"), "a") as f:
        f.write("### sec-3 lowercase id\n- where: does/not/exist.ts:999\n- severity: catastrophic\n\n"
                + FINDING.replace("MONEY-1", "LOL-1").replace("src/scan/quota.ts:13", "/etc/hosts:1")
                .replace("counter-integrity", "secrets").replace("CONFIRMED (repro/quota.test.js)", "CONFIRMED (")
                + FINDING.replace("MONEY-1", "LOL-10").replace("counter-integrity", "secrets")
                .replace("CONFIRMED (repro/quota.test.js)", "PLAUSIBLE (reasoned, not run)"))
    write(os.path.join(out, "SCAN.md"), "".join(f"- **{name}** fires: always\n" for name in lenses))
    write(os.path.join(out, "REPORT.md"), "Nothing to fix. LOL-10 is fine.\n")
    return out


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
                        "CONFIRMED verdict names no reproduction file"):
            self.assertIn(problem, out)

    def test_report_must_place_every_finding(self):
        code, out = run(FINDING + CLEAN, report="nothing here")
        self.assertEqual(code, 1)
        self.assertIn("REPORT.md does not place MONEY-1", out)

    def test_missing_output_directory_fails(self):
        code, out = verify(os.path.join(tempfile.mkdtemp(), "never-ran"))
        self.assertEqual(code, 1, out)
        self.assertIn("no such output directory", out)

    def test_no_findings_and_no_scan_fail(self):
        empty = tempfile.mkdtemp()
        os.makedirs(os.path.join(empty, "findings"))
        code, out = verify(empty)
        self.assertEqual(code, 1, out)
        self.assertIn("no findings file was checked", out)
        self.assertIn("SCAN.md is missing", out)

    def test_garbage_audit_fails(self):
        code, out = verify(garbage_audit())
        self.assertEqual(code, 1, out)
        for problem in ("LOL-1: where path '/etc/hosts' is outside the repo",
                        "LOL-1: CONFIRMED verdict names no reproduction file",
                        "heading '### sec-3 lowercase id' is not '### LENS-1 claim'",
                        "REPORT.md does not place LOL-1\n",
                        "REPORT.md exists but refuted.md does not"):
            self.assertIn(problem, out)

    def test_confirmed_needs_a_reproduction_file_that_exists(self):
        code, out = run(FINDING.replace("repro/quota.test.js", "repro/never-written.test.js") + CLEAN)
        self.assertEqual(code, 1, out)
        self.assertIn("CONFIRMED verdict names no reproduction file", out)

    def test_refuted_finding_cannot_stay_in_findings(self):
        code, out = run(FINDING + CLEAN, report="- MONEY-1", refuted="MONEY-1: guarded upstream\n")
        self.assertEqual(code, 1, out)
        self.assertIn("MONEY-1 is in refuted.md and still in findings", out)

    def test_blank_severity_is_a_missing_field_not_a_crash(self):
        code, out = run(FINDING.replace("- severity: high", "- severity:  ") + CLEAN)
        self.assertEqual(code, 1, out)
        self.assertIn("missing field 'severity'", out)
        self.assertNotIn("Traceback", out)

    def test_where_path_with_spaces(self):
        root = tempfile.mkdtemp()
        write(os.path.join(root, "src dir", "my file.ts"), "a\nb\n")
        code, out = run(FINDING.replace("src/scan/quota.ts:13", "src dir/my file.ts:2") + CLEAN, root=root)
        self.assertEqual(code, 0, out)


if __name__ == "__main__":
    unittest.main()
