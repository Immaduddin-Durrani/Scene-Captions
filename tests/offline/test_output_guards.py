"""Reproductions for structural guards; no model or network requests."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
from nim_client import parse_json
from generation.variants import GRID_KEYS, validate_item

class OutputGuardTests(unittest.TestCase):
    def test_missing_finish_reason_is_not_a_completed_generation(self):
        for reason in [None, 'length', 'content_filter', 'tool_calls']:
            response = {'choices':[{'finish_reason':reason,'message':{'content':'{"items": []}'}}]}
            with self.subTest(reason=reason), self.assertRaisesRegex(ValueError,'completion'):
                parse_json(response)
        self.assertEqual(parse_json({'choices':[{'finish_reason':'stop','message':{'content':'{"items": []}'}}]}), {'items':[]})

    def test_truncated_completion_is_not_a_valid_candidate_even_if_json_parses(self):
        response = {'choices': [{'finish_reason': 'length', 'message': {'content': '{"items": []}'}}]}
        with self.assertRaisesRegex(ValueError, 'completion'):
            parse_json(response)

    def test_one_bracket_line_cannot_hide_an_extra_event_or_empty_label(self):
        for text in ['[music] [wind]', '[music][wind]', '[]', '[   ]']:
            item = {'id': 'one-sound', 'grid': {key: text for key in GRID_KEYS}, 'plain': text}
            with self.subTest(text=text), self.assertRaises(ValueError):
                validate_item(item, 'one-sound', 280)
