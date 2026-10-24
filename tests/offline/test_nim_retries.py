"""Retry behavior is simulated; these tests never call NVIDIA or actually sleep."""
import io
import sys
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import nim_client


def http_error(code, headers=None):
    return urllib.error.HTTPError("https://example.invalid", code, "test", headers or {}, io.BytesIO(b"test-key"))


class RetryTests(unittest.TestCase):
    def test_rate_limit_backoff_is_bounded_at_one_minute(self):
        with patch.object(nim_client, "api_key", return_value="test-key"), patch.object(nim_client, "rate_limit", create=True) as pacing, patch.object(nim_client.urllib.request, "urlopen", side_effect=[http_error(429) for _ in range(7)]) as send, patch.object(nim_client.time, "sleep") as sleep:
            with self.assertRaisesRegex(RuntimeError, "NVIDIA HTTP 429") as error:
                nim_client.request("test")
            self.assertEqual(send.call_count, 7)
            self.assertEqual(pacing.call_count, 7)
            self.assertEqual([call.args[0] for call in sleep.call_args_list], [2, 4, 8, 16, 32, 60])
            self.assertNotIn("test-key", str(error.exception))

    def test_bad_request_is_not_retried(self):
        with patch.object(nim_client, "api_key", return_value="test-key"), patch.object(nim_client, "rate_limit", create=True), patch.object(nim_client.urllib.request, "urlopen", side_effect=http_error(400)) as send, patch.object(nim_client.time, "sleep") as sleep:
            with self.assertRaisesRegex(RuntimeError, "HTTP 400"):
                nim_client.request("test")
            self.assertEqual(send.call_count, 1)
            sleep.assert_not_called()

    def test_retry_after_is_honored_within_the_cap(self):
        with patch.object(nim_client, "api_key", return_value="test-key"), patch.object(nim_client, "rate_limit", create=True), patch.object(nim_client.urllib.request, "urlopen", side_effect=[http_error(429, {"Retry-After": "10"}), io.BytesIO(b'{"ok":true}')]), patch.object(nim_client.time, "sleep") as sleep:
            self.assertTrue(nim_client.request("test")["ok"])
            sleep.assert_called_once_with(10)

    def test_long_retry_after_stops_instead_of_retrying_early(self):
        with patch.object(nim_client, "api_key", return_value="test-key"), patch.object(nim_client, "rate_limit", create=True), patch.object(nim_client.urllib.request, "urlopen", side_effect=http_error(429, {"Retry-After": "120"})) as send, patch.object(nim_client.time, "sleep") as sleep:
            with self.assertRaisesRegex(RuntimeError, "Retry-After exceeds"):
                nim_client.request("test")
            self.assertEqual(send.call_count, 1)
            sleep.assert_not_called()

    def test_temporary_network_failure_can_recover(self):
        with patch.object(nim_client, "api_key", return_value="test-key"), patch.object(nim_client, "rate_limit", create=True), patch.object(nim_client.urllib.request, "urlopen", side_effect=[urllib.error.URLError("temporary"), io.BytesIO(b'{"ok":true}')]), patch.object(nim_client.time, "sleep") as sleep:
            self.assertTrue(nim_client.request("test")["ok"])
            sleep.assert_called_once_with(2)

    def test_response_wait_is_separate_from_backoff(self):
        for thinking, override, expected in [(False, None, 180), (True, None, 300), (True, 600, 600)]:
            with patch.object(nim_client, "api_key", return_value="test-key"), patch.object(nim_client, "rate_limit"), patch.object(nim_client.urllib.request, "urlopen", return_value=io.BytesIO(b'{"ok":true}')) as send:
                self.assertTrue(nim_client.request("test", thinking=thinking, timeout=override)["ok"])
                self.assertEqual(send.call_args.kwargs["timeout"], expected)


if __name__ == "__main__":
    unittest.main()
