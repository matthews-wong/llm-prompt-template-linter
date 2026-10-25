import contextlib
import io
import os
import tempfile
import unittest

from promptlint.__main__ import main

TEMPLATE = "---\nname: hi\nversion: 1.0.0\nvariables: [who]\n---\nHello {{who}}\n"


class CliTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)
        self.path = os.path.join(self.dir.name, "hi.prompt")

    def write(self, text):
        with open(self.path, "w", encoding="utf-8") as handle:
            handle.write(text)

    def run_main(self, argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = main(argv)
        return code, out.getvalue(), err.getvalue()

    def test_clean_directory_exits_zero(self):
        self.write(TEMPLATE)
        code, out, _ = self.run_main([self.dir.name])
        self.assertEqual(code, 0)
        self.assertIn("0 finding(s)", out)

    def test_findings_exit_one(self):
        self.write(TEMPLATE.replace("1.0.0", "x"))
        code, out, _ = self.run_main([self.dir.name])
        self.assertEqual(code, 1)
        self.assertIn("PL002", out)

    def test_empty_directory_is_an_error(self):
        code, _, err = self.run_main([self.dir.name])
        self.assertEqual(code, 1)
        self.assertIn("no .prompt files", err)

    def test_render_fills_values(self):
        self.write(TEMPLATE)
        code, out, _ = self.run_main(["--render", self.path, "who=world"])
        self.assertEqual((code, out.strip()), (0, "Hello world"))

    def test_render_reports_missing_value(self):
        self.write(TEMPLATE)
        code, _, err = self.run_main(["--render", self.path])
        self.assertEqual(code, 1)
        self.assertIn("who", err)


if __name__ == "__main__":
    unittest.main()
