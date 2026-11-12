"""One small synthetic project per routing mistake scan.py used to make. Run: python3 -m unittest discover tests"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCAN = os.path.join(ROOT, "skills", "audit", "scripts", "scan.py")
sys.path.insert(0, os.path.dirname(SCAN))
import scan as scan_module  # noqa: E402


class RoutingTest(unittest.TestCase):
    def project(self, files):
        root = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, root)
        for path, text in files.items():
            full = os.path.join(root, path)
            os.makedirs(os.path.dirname(full), exist_ok=True)
            with open(full, "w") as f:
                f.write(text)
        return root

    def scan(self, files):
        return subprocess.run([sys.executable, SCAN, self.project(files)], capture_output=True, text=True, check=True).stdout

    def test_vercel_ai_sdk_fires_the_ai_lens(self):
        out = self.scan({"package.json": json.dumps({"dependencies": {"ai": "^4.3.0", "@ai-sdk/google": "^1.2.0"}}),
                         "src/digest.ts": "const r = await generateText({ model, prompt })\n"})
        self.assertIn("- **ai** fires: ai (package.json); ai-code (src/digest.ts)", out)

    def test_ocr_dependency_is_ai_not_money(self):
        out = self.scan({"requirements.txt": "paddleocr==2.7\npaddlepaddle==2.6\n", "ocr.py": "import paddleocr\n"})
        self.assertIn("- **ai** fires", out)
        self.assertIn("- money skipped", out)

    def test_serverless_functions_and_blob_storage_fire_the_data_lens(self):
        out = self.scan({"package.json": json.dumps({"dependencies": {"@vercel/blob": "^2.0.0"}}),
                         "api/desk.js": "module.exports = async function (req, res) { res.end('ok') }\n"})
        self.assertIn("database-dep (package.json)", out)
        self.assertIn("server-api (api/desk.js)", out)
        self.assertIn("api-dir (api/desk.js)", out)

    def test_stdlib_http_server_fires_the_data_lens(self):
        out = self.scan({"app.py": "from http.server import BaseHTTPRequestHandler\n\nclass H(BaseHTTPRequestHandler):\n    pass\n"})
        self.assertIn("- **data** fires: server-api (app.py)", out)

    def test_static_html_is_source_with_a_ui(self):
        out = self.scan({"index.html": "<!doctype html>\n<script>document.body.innerHTML = location.hash</script>\n"})
        self.assertIn("1 source files in scope", out)
        self.assertIn("- **ux** fires: ui (index.html)", out)
        self.assertIn("index.html:2: innerHTML =", out)

    def test_go_service_gets_data_lens_and_sites(self):
        out = self.scan({"go.mod": "module x\n", "main.go": (
            'package main\nimport ("database/sql"; "net/http"; "os/exec")\n'
            'func h(w http.ResponseWriter, r *http.Request) {\n'
            '\trows, _ := db.Query("SELECT id FROM users WHERE id = " + r.URL.Query().Get("id"))\n'
            '\texec.Command("sh", "-c", r.URL.Query().Get("cmd"))\n}\n'
            'func main() { http.HandleFunc("/", h); http.ListenAndServe(":8080", nil) }\n')})
        self.assertIn("- **data** fires: server-api (main.go); database-code (main.go)", out)
        self.assertIn("`security.injection` (2 hits)", out)
        self.assertIn("`failure.silent-catch` (1 hits)", out)

    def test_shell_scripts_count_as_source(self):
        self.assertIn("languages: sh 1", self.scan({"hooks/guard.sh": "#!/bin/sh\nsleep 1\n"}))

    def test_fixture_projects_do_not_route_the_real_one(self):
        out = self.scan({"tool.py": "print('x')\n",
                         "tests/fixtures/shop/package.json": json.dumps({"dependencies": {"stripe": "1", "react": "18"}}),
                         "tests/fixtures/shop/App.swift": "import SwiftUI\n"})
        self.assertIn("- stacks: python (tool.py)", out)
        self.assertIn("- money skipped", out)
        self.assertIn("- ux skipped", out)
        self.assertIn("- not read for routing: tests/fixtures/ (2)", out)

    def test_lockfile_is_not_seeded_but_still_selects_analyzers(self):
        lock = json.dumps({"packages": {f"node_modules/p{i}": {"dependencies": {"q": "^1.0.0"}} for i in range(50)}}, indent=1)
        out = self.scan({"package.json": json.dumps({"dependencies": {"left-pad": "^1.3.0"}}), "package-lock.json": lock})
        self.assertIn("`security.supply-chain` (1 hits)", out)
        self.assertIn("package-lock.json (1)", out)
        self.assertIn("**npm-audit**", out)

    def test_skipped_build_folder_is_reported(self):
        out = self.scan({"skills/build/make.py": "print('x')\n", "skills/plan/plan.py": "print('y')\n"})
        self.assertIn("- not read for routing: skills/build/ (1)", out)

    def test_hoisted_local_binary_is_available(self):
        root = self.project({"package.json": "{}", "node_modules/.bin/tsc": "", "packages/web/tsconfig.json": "{}"})
        subprocess.run(["git", "-C", root, "init", "-q"], check=True)
        self.assertTrue(scan_module.tool_available(os.path.join(root, "packages", "web"), "npx --no-install tsc --noEmit"))
        self.assertFalse(scan_module.tool_available(os.path.join(root, "packages", "web"), "npx --no-install eslint ."))

    def test_no_analyzer_command_downloads_its_rules(self):
        self.assertFalse([t.name for t in scan_module.load_tools() if "--config p/" in t.command])


if __name__ == "__main__":
    unittest.main()
