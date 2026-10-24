"""Local credential resolution; no network requests and no real key access."""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import nim_client


class CredentialTests(unittest.TestCase):
    def test_alias_in_local_env_file_is_supported(self):
        with patch.object(Path, "exists", return_value=True), patch.object(Path, "read_text", return_value='NVIDIA_KEY="test-only-value"\n'), patch.dict("os.environ", {}, clear=True):
            self.assertEqual(nim_client.api_key(), "test-only-value")

    def test_process_value_takes_precedence_over_local_file(self):
        with patch.object(Path, "exists", return_value=True), patch.object(Path, "read_text", return_value="NVIDIA_API_KEY=old-file-value\n"), patch.dict("os.environ", {"NVIDIA_KEY": "process-value"}, clear=True):
            self.assertEqual(nim_client.api_key(), "process-value")

    def test_missing_key_has_no_secret_in_error(self):
        with patch.object(Path, "exists", return_value=False), patch.dict("os.environ", {}, clear=True):
            with self.assertRaisesRegex(RuntimeError, "NVIDIA_API_KEY or NVIDIA_KEY"):
                nim_client.api_key()


if __name__ == "__main__":
    unittest.main()
