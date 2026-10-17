import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("upsert.py")
URL = "https://github.com/OnFlyApp/ext-parser-go/releases/download/v1.0.0/go-parser.wasm"
SHA = "a" * 64


def run(path, *args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(path), *args],
        text=True, capture_output=True,
    )


class UpsertTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.path = Path(self.dir.name) / "registry.json"
        self.path.write_text("{}\n")

    def tearDown(self):
        self.dir.cleanup()

    def upsert(self, version="1.0.0", url=URL, sha=SHA, extensions=".go"):
        return run(
            self.path, "--plugin", "go", "--version", version,
            "--url", url, "--sha256", sha, "--extensions", extensions,
        )

    def test_adds_go_and_sets_latest(self):
        result = self.upsert()
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(self.path.read_text())
        self.assertEqual(data["go"]["latest"], "1.0.0")
        self.assertEqual(data["go"]["versions"]["1.0.0"]["sha256"], SHA)
        self.assertEqual(data["go"]["versions"]["1.0.0"]["extensions"], [".go"])
        self.assertTrue(self.path.read_text().endswith("\n"))

    def test_same_release_is_noop(self):
        self.assertEqual(self.upsert().returncode, 0)
        before = self.path.read_text()
        self.assertEqual(self.upsert().returncode, 0)
        self.assertEqual(self.path.read_text(), before)

    def test_checksum_change_keeps_file(self):
        self.assertEqual(self.upsert().returncode, 0)
        before = self.path.read_bytes()
        result = self.upsert(sha="b" * 64)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.path.read_bytes(), before)

    def test_older_tag_does_not_move_latest(self):
        self.assertEqual(self.upsert(version="1.2.9", url=URL.replace("v1.0.0", "v1.2.9")).returncode, 0)
        self.assertEqual(self.upsert(version="1.2.10", url=URL.replace("v1.0.0", "v1.2.10")).returncode, 0)
        result = self.upsert(version="1.2.0", url=URL.replace("v1.0.0", "v1.2.0"))
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(self.path.read_text())
        self.assertEqual(data["go"]["latest"], "1.2.10")
        self.assertIn("1.2.0", data["go"]["versions"])

    def test_rejects_prerelease_and_markdown_url(self):
        before = self.path.read_bytes()
        bad_ver = self.upsert(version="1.0.0-rc.1")
        self.assertNotEqual(bad_ver.returncode, 0)
        wrapped = "[" + URL + "](" + URL + ")"
        bad_url = self.upsert(url=wrapped)
        self.assertNotEqual(bad_url.returncode, 0)
        self.assertEqual(self.path.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
