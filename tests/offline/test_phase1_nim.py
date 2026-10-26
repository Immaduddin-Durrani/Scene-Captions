"""Offline checks of experiment media encoding/redaction; no real key or API use."""
import base64
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import wave

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('phase1_nim', ROOT / 'scripts/diagnostics/phase1_nim.py')
nim = importlib.util.module_from_spec(spec)
spec.loader.exec_module(nim)


class MediaContractTests(unittest.TestCase):
    def test_both_shapes_encode_identical_wav_and_report_hash(self):
        with tempfile.TemporaryDirectory(dir=ROOT / 'artifacts') as directory:
            p = Path(directory) / 'fixture.wav'
            with wave.open(str(p), 'wb') as w:
                w.setnchannels(1); w.setsampwidth(2); w.setframerate(16000)
                w.writeframes(b'\0\0' * 1600)
            a, ma = nim.audio_part(p)
            b, mb = nim.audio_part(p, 'input_audio')
            self.assertEqual(base64.b64decode(a['audio_url']['url'].split(',')[1]), p.read_bytes())
            self.assertEqual(base64.b64decode(b['input_audio']['data']), p.read_bytes())
            self.assertEqual(ma['sha256'], mb['sha256'])
            self.assertEqual(ma['duration_s'], .1)
            with self.assertRaises(ValueError):
                nim.audio_part(p, 'unsupported')

    def test_report_redaction_removes_inline_bytes_without_mutating_request(self):
        parts = [{'type':kind,kind:{'url':'data:audio/wav;base64,PRIVATE_MEDIA'}}
                 for kind in ['audio_url','video_url','image_url']]
        parts.append({'type':'input_audio','input_audio':{'data':'PRIVATE_MEDIA','format':'wav'}})
        payload = {'messages':[{'role':'user','content':parts}]}
        before = json.dumps(payload)
        summary = nim.summarize(payload)
        self.assertNotIn('PRIVATE_MEDIA', json.dumps(summary))
        self.assertEqual(json.dumps(payload), before)
        self.assertEqual(summary['messages'][0]['content'][-1]['input_audio']['format'], 'wav')


if __name__ == '__main__':
    unittest.main()
