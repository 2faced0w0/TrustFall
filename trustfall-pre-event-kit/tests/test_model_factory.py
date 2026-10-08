import os
import unittest
from unittest.mock import patch

from models.base import ModelConfigurationError
from models.factory import create_model
from models.mock import MockAdapter


class ModelFactoryTests(unittest.TestCase):
    def test_mock_provider(self) -> None:
        with patch.dict(os.environ, {"TRUSTFALL_PROVIDER": "mock"}, clear=True):
            self.assertIsInstance(create_model(), MockAdapter)

    def test_unknown_provider_fails_clearly(self) -> None:
        with self.assertRaisesRegex(ModelConfigurationError, "Unknown provider"):
            create_model("not-a-provider")

    def test_missing_live_configuration_does_not_leak_secret(self) -> None:
        marker = "do-not-leak-this-value"
        with patch("models.factory._load_dotenv"), patch.dict(
            os.environ,
            {"TRUSTFALL_PROVIDER": "groq", "GROQ_API_KEY": marker},
            clear=True,
        ):
            with self.assertRaises(ModelConfigurationError) as caught:
                create_model()
        self.assertNotIn(marker, str(caught.exception))
        self.assertIn("model is not configured", str(caught.exception))


if __name__ == "__main__":
    unittest.main()
