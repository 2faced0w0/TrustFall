import copy
import json
import tempfile
import unittest
from pathlib import Path


class FilesystemTests(unittest.TestCase):
    def test_temporary_json_snapshot_is_isolated(self) -> None:
        original = {"items": [{"id": "demo", "value": "original"}]}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "source.json"
            path.write_text(json.dumps(original), encoding="utf-8")
            snapshot = copy.deepcopy(json.loads(path.read_text(encoding="utf-8")))
            snapshot["items"][0]["value"] = "changed"
            loaded_again = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(loaded_again, original)
            self.assertNotEqual(snapshot, original)


if __name__ == "__main__":
    unittest.main()
