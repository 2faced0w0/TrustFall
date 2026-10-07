import importlib
import hashlib
import unittest
from pathlib import Path


class ImportTests(unittest.TestCase):
    def test_project_imports(self) -> None:
        modules = [
            "smoke.smoke_app",
            "models.base",
            "models.factory",
            "models.mock",
            "models.google",
            "models.mistral",
            "models.deepseek",
            "models.cohere",
            "models.groq",
            "models.openrouter",
            "models.freellmapi",
        ]
        for module in modules:
            with self.subTest(module=module):
                importlib.import_module(module)

    def test_sibling_models_packages_are_byte_identical_when_present(self) -> None:
        root = Path(__file__).resolve().parents[2]
        left = root / "trustfall-pre-event-kit" / "models"
        right = root / "trustfall-survive-it" / "models"
        if not right.is_dir():
            self.skipTest("sibling Survive It kit is not present in this distribution")

        def package_hashes(folder: Path) -> dict[str, str]:
            return {
                path.relative_to(folder).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
                for path in sorted(folder.rglob("*.py"))
            }

        self.assertEqual(package_hashes(left), package_hashes(right))


if __name__ == "__main__":
    unittest.main()
