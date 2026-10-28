"""Bounded explicit NIM requests, with a shared 14-request ceiling for this pilot."""
import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--manifest', type=Path, required=True); p.add_argument('--report', type=Path, required=True)
    a = p.parse_args(); manifest = a.manifest.resolve(); out = a.report.resolve()
    assert manifest.is_relative_to(HERE / 'inputs') and out.is_relative_to(HERE / 'reports') and not out.exists()
    jobs = json.loads(manifest.read_text()); assert 1 <= len(jobs) <= 8
    spec = importlib.util.spec_from_file_location('bounded_nim_driver', ROOT / 'scripts/diagnostics/phase1_nim.py')
    driver = importlib.util.module_from_spec(spec); spec.loader.exec_module(driver)
    rows, consecutive_capacity = [], 0
    for job in jobs:
        observed = sum(len(json.loads(path.read_text()).get('calls', [])) for path in (HERE / 'reports').glob('*.json'))
        assert observed < 14, 'Hard request ceiling reached'
        payload = copy.deepcopy(job['payload']); media = []
        for message in payload.get('messages', []):
            if not isinstance(message.get('content'), list):
                continue
            for index, part in enumerate(message['content']):
                if part['type'] == 'local_wav':
                    message['content'][index], info = driver.audio_part(ROOT / part['path']); media.append(info)
                elif part['type'] == 'local_jpeg':
                    message['content'][index], info = driver.image_part(ROOT / part['path']); media.append(info)
        row = {'case': job['case'], 'fixtures': media, **driver.run_one(payload)}; rows.append(row)
        consecutive_capacity = consecutive_capacity + 1 if row.get('http_status') in [429, 503] else 0
        out.write_text(json.dumps({'scope': 'NVIDIA audio-first recognition and constrained late visual association',
            'manifest_sha256': hashlib.sha256(manifest.read_bytes()).hexdigest(), 'calls': rows,
            'stopped_on_capacity': consecutive_capacity >= 3}, indent=2) + '\n')
        choice = (row.get('response', {}).get('choices') or [{}])[0]
        print(job['case'], row.get('http_status'), choice.get('finish_reason'),
              repr(choice.get('message', {}).get('content')), row.get('error', ''), flush=True)
        if consecutive_capacity >= 3 or row.get('http_status') in [401, 403]:
            break


if __name__ == '__main__':
    main()
