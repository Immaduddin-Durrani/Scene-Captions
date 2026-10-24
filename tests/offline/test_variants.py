import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from generation.variants import GRID_KEYS, character_budget, reading_flags, validate_item, validate_batch


class VariantTests(unittest.TestCase):
    def test_missing_cells_and_extra_cells_are_rejected(self):
        item = {"id": "cue-1", "grid": {key: "[music]" for key in GRID_KEYS}, "plain": "[music]"}
        self.assertEqual(validate_item(item, "cue-1", 30)["plain"], "[music]")
        item["grid"]["4-1"] = "[music]"
        with self.assertRaises(ValueError):
            validate_item(item, "cue-1", 30)

    def test_identity_and_length_must_match_the_source_job(self):
        item = {"id": "wrong-cue", "grid": {key: "[music]" for key in GRID_KEYS}, "plain": "[music]"}
        with self.assertRaises(ValueError):
            validate_item(item, "cue-1", 30)
        item["id"] = "cue-1"
        with self.assertRaises(ValueError):
            validate_item(item, "cue-1", 6)

    def test_reading_flags_do_not_change_source_timing(self):
        cue = {"cue_id": "cue-1", "start_s": 1, "end_s": 1.5, "original_text": "[wings flap]", "grid": {"3-3": "[A bird flaps its wings]"}}
        self.assertTrue(reading_flags([cue]))
        self.assertEqual(cue["end_s"], 1.5)
        self.assertGreaterEqual(character_budget(cue), len(cue["original_text"]))

    def test_simultaneous_sound_must_not_disappear(self):
        item = {"id": "two-sounds", "grid": {key: "[brook babbles]" for key in GRID_KEYS}, "plain": "[brook babbles]"}
        with self.assertRaisesRegex(ValueError, "simultaneous sound"):
            validate_item(item, "two-sounds", 280, expected_lines=2)

    def test_echoing_the_source_is_not_useful_personalization(self):
        jobs = [{"id": "sound-1", "source": "[serene music]", "max_characters": 40}]
        items = [{"id": "sound-1", "grid": {key: "[serene music]" for key in GRID_KEYS}, "plain": "[music]"}]
        with self.assertRaisesRegex(ValueError, "only copied"):
            validate_batch(items, jobs)


if __name__ == "__main__":
    unittest.main()
