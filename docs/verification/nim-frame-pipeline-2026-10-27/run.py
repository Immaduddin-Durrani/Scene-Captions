"""Run only the eight frozen NVIDIA comparisons; stop on three capacity failures."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def main():
    out = HERE / 'reports/comparisons.json'
    assert not out.exists(), 'Preserve completed report'
    manifest = HERE / 'inputs/manifest.json'
    protocol = json.loads((HERE / 'protocol.json').read_text())
    digest = hashlib.sha256(manifest.read_bytes()).hexdigest()
    assert digest == protocol['manifest_sha256']
    jobs = json.loads(manifest.read_text()); assert len(jobs) == 8
    spec = importlib.util.spec_from_file_location('nim_frames_driver', ROOT / 'scripts/diagnostics/phase1_nim.py')
    driver = importlib.util.module_from_spec(spec); spec.loader.exec_module(driver)
    rows, capacity = [], 0
    for job in jobs:
        payload = copy.deepcopy(job['payload']); fixtures = []
        for message in payload['messages']:
            for i, part in enumerate(message['content']):
                if part['type'] == 'local_wav':
                    message['content'][i], meta = driver.audio_part(ROOT / part['path'])
                    fixtures.append(meta)
                elif part['type'] == 'local_jpeg':
                    message['content'][i], meta = driver.image_part(ROOT / part['path'])
                    fixtures.append(meta)
        row = {'case': job['case'], 'fixtures': fixtures, **driver.run_one(payload)}
        rows.append(row)
        capacity = capacity + 1 if row.get('http_status') in [429, 503] else 0
        out.write_text(json.dumps({'scope': 'Actual audio with event-triggered matching frames; no source-caption inputs or playback installation',
            'manifest_sha256': digest, 'calls': rows, 'stopped_on_capacity': capacity >= 3}, indent=2) + '\n')
        choice = (row.get('response', {}).get('choices') or [{}])[0]
        print(job['case'], row.get('http_status'), choice.get('finish_reason'),
              repr(choice.get('message', {}).get('content')), row.get('error', ''), flush=True)
        if capacity >= 3 or row.get('http_status') in [401, 403]:
            break


if __name__ == '__main__':
    main()
