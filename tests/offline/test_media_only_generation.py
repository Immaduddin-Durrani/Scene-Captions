"""Offline guards for opt-in media-only exports; no NVIDIA calls."""
import importlib.util
import json
import io
import sys
import urllib.error
from email.message import Message
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location('media_only', ROOT / 'scripts/generate-media-only.py')
generator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(generator)


class MediaOnlyGuards(unittest.TestCase):
    def test_capacity_metadata_preserves_retry_after_without_auth_headers(self):
        driver = sys.modules['phase1_nim']
        headers = Message()
        headers['Retry-After'] = '5'
        headers['Authorization'] = 'private-value'
        failure = urllib.error.HTTPError('https://example.invalid', 503, 'busy', headers, io.BytesIO(b'busy'))
        with patch.object(driver, 'api_key', return_value='private-key'), patch.object(driver, 'rate_limit'), patch.object(driver.urllib.request, 'urlopen', side_effect=failure):
            row = driver.run_one({'model': 'test', 'messages': []})
        self.assertEqual(row['response_headers'], {'Retry-After': '5'})
        self.assertNotIn('private', json.dumps(row))

    def test_renderer_accepts_identical_complete_duplicates_only(self):
        value = {'captions': [{'id': '0', 'essential': 'Music', 'balanced': 'Music', 'detailed': 'Music'}]}
        compact = json.dumps(value)
        response = lambda text, finish='stop': {'choices': [{'finish_reason': finish, 'message': {'content': text}}]}
        self.assertEqual(generator.parse_render_response(response(compact + '\n' + json.dumps(value, indent=2))), value)
        for text, finish in ((compact + '\n' + '{', 'stop'), (compact + '\n' + '{"captions":[]}', 'stop'),
                             (compact + '\nNote: complete', 'stop'), (compact, 'length')):
            with self.assertRaises(ValueError):
                generator.parse_render_response(response(text, finish))
        with self.assertRaises(ValueError):
            generator.validate_rendered(value, ['different-id'])
        with self.assertRaises(ValueError):
            generator.validate_rendered({'captions': value['captions'] * 2}, ['0', '1'])

    def test_sound_times_never_escape_their_window(self):
        cue = dict(start_s=0, end_s=15, essential='Music', balanced='Strings play', detailed='Sustained strings play')
        self.assertEqual(len(generator.validate_sounds({'cues': [cue]}, 15)), 1)
        for invalid in (float('nan'), float('inf'), True, 15.01):
            with self.assertRaises(ValueError):
                generator.validate_sounds({'cues': [{**cue, 'end_s': invalid}]}, 15)

    def test_markup_and_oversized_captions_are_rejected(self):
        cue = dict(start_s=0, end_s=1, essential='Music', balanced='Music', detailed='Music')
        for text in ('[music]', '<script>', 'line\nbreak', 'x' * 279, ''):
            with self.assertRaises(ValueError):
                generator.validate_sounds({'cues': [{**cue, 'essential': text}]}, 1)

    def test_speech_uses_reported_milliseconds_and_clip_offset(self):
        response = {'results': [{'alternatives': [{'transcript': 'A word.', 'words': [
            {'word': 'A', 'end_time': 100},
            {'word': 'word.', 'start_time': 100, 'end_time': 500}]}]}]}
        cues, rejected = generator.dialogue_cues(response, 30, 15)
        self.assertEqual(cues, [{'start_s': 30, 'end_s': 30.5, 'text': 'A word.'}])
        self.assertFalse(rejected)

    def test_unknown_tokens_and_missing_times_are_not_invented_dialogue(self):
        for alternative in ({'transcript': '<unk><unk>', 'words': []},
                            {'transcript': 'Hello', 'words': []},
                            {'transcript': 'Hello', 'words': [{'word': 'Hello', 'end_time': 16000}]}):
            cues, rejected = generator.dialogue_cues({'results': [{'alternatives': [alternative]}]}, 0, 15)
            self.assertFalse(cues)
            self.assertTrue(rejected)

    def test_long_speech_is_grouped_without_word_loss(self):
        words = [{'word': f'word{i}', 'start_time': i * 500, 'end_time': i * 500 + 300} for i in range(24)]
        cues, rejected = generator.dialogue_cues({'results': [{'alternatives': [{'transcript': 'spoken words', 'words': words}]}]}, 60, 15)
        self.assertEqual(' '.join(c['text'] for c in cues), ' '.join(w['word'] for w in words))
        self.assertTrue(all(60 <= c['start_s'] < c['end_s'] <= 75 and c['end_s'] - c['start_s'] <= 6 for c in cues))
        self.assertFalse(rejected)


if __name__ == '__main__':
    unittest.main()
