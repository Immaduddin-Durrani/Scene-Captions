"""Source rewrite guards only; no NVIDIA calls or source editing."""
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('source_richness', ROOT/'scripts/generate-source-richness.py')
generator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generator)


class SourceRichness(unittest.TestCase):
    def setUp(self):
        self.inputs = [{'id': '0', 'reference': '[APPLE THUDS]', 'max_characters': {'essential': 20, 'balanced': 30, 'rich': 40}}]
        self.value = {'captions': [{'id': '0', 'essential': 'Thud', 'balanced': 'An apple thuds', 'rich': 'An apple makes a thudding sound'}]}

    def test_drafts_do_not_bypass_final_word_checks(self):
        jargon = {'captions': [{**self.value['captions'][0], 'rich': 'An ethereal harmonic resonance'}]}
        self.assertTrue(generator.validate_drafts(jargon, self.inputs))
        with self.assertRaises(ValueError):
            generator.validate(jargon, self.inputs)

    def test_changed_ids_and_markup_are_rejected_before_review(self):
        self.assertTrue(generator.validate(self.value, self.inputs))
        for change in ({'id': 'other'}, {'rich': '<script>'}, {'rich': 'a\nline'}, {'rich': 'a'*181}):
            with self.assertRaises(ValueError):
                generator.validate_drafts({'captions': [{**self.value['captions'][0], **change}]}, self.inputs)

    def test_completion_and_duplicate_json_guards(self):
        text = json.dumps(self.value)
        response = lambda t, f='stop': {'choices': [{'finish_reason': f, 'message': {'content': t}}]}
        self.assertEqual(generator.parse_response(response(text+'\n'+text)), self.value)
        for t, finish in ((text, 'length'), (text+'\n{}', 'stop'), (text+'\n{', 'stop'), (text+'\nExplanation', 'stop')):
            with self.assertRaises(ValueError):
                generator.parse_response(response(t, finish))

    def test_unknown_scene_details_are_blocked_and_feedback_is_specific(self):
        value = {'captions': [{**self.value['captions'][0], 'rich': 'A heavy apple hits ground'}]}
        with self.assertRaises(ValueError):
            generator.validate(value, self.inputs)
        critique = generator.feedback(value, self.inputs)
        self.assertIn('0 rich', critique)
        self.assertIn('unsupported detail heavy', critique)
        self.assertIn('[APPLE THUDS]', critique)


if __name__ == '__main__':
    unittest.main()
