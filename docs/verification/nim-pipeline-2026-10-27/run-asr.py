"""Bounded NVIDIA Whisper gRPC probe; credentials remain private; no installation."""
import argparse
import hashlib
import json
import sys
import time
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'scripts'))
from nim_client import api_key, rate_limit


def main():
    import grpc
    import riva.client
    from google.protobuf.json_format import MessageToDict
    from riva.client.proto import riva_asr_pb2
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--cases', nargs='+', required=True)
    p.add_argument('--report', type=Path, required=True)
    p.add_argument('--no-word-times', action='store_true')
    p.add_argument('--model', choices=['whisper', 'parakeet'], default='whisper')
    p.add_argument('--raw-pcm', action='store_true')
    args = p.parse_args()
    here = Path(__file__).resolve().parent
    path = here / 'inputs/asr.json'
    jobs = json.loads(path.read_text())
    assert set(args.cases) <= {j['case'] for j in jobs} and len(args.cases) <= 5
    out = args.report.resolve()
    assert out.is_relative_to(here / 'reports') and not out.exists()
    key = api_key()
    function_id = ('b702f636-f60c-4a3d-a6f4-f3568c13bd7d' if args.model == 'whisper'
                   else 'd3fe9151-442b-4204-a70d-5fcc597fd610')
    auth = riva.client.Auth(use_ssl=True, uri='grpc.nvcf.nvidia.com:443', metadata_args=[
        ['function-id', function_id], ['authorization', 'Bearer ' + key]])
    service = riva.client.ASRService(auth)
    calls = []
    config = riva.client.RecognitionConfig(language_code='en' if args.model == 'whisper' else 'en-US', sample_rate_hertz=16000,
        audio_channel_count=1, max_alternatives=1, enable_automatic_punctuation=True,
        enable_word_time_offsets=not args.no_word_times)
    if args.raw_pcm:
        config.encoding = riva.client.AudioEncoding.LINEAR_PCM
    try:
        for job in jobs:
            if job['case'] not in args.cases:
                continue
            media = ROOT / job['file']
            raw = media.read_bytes()
            assert hashlib.sha256(raw).hexdigest() == job['sha256']
            with wave.open(str(media), 'rb') as w:
                assert (w.getnchannels(), w.getsampwidth(), w.getframerate()) == (1, 2, 16000)
                assert w.getnframes() / 16000 <= 30
                if args.raw_pcm:
                    raw = w.readframes(w.getnframes())
            request = riva_asr_pb2.RecognizeRequest(config=config, audio=raw)
            row = {'case': job['case'], 'fixture': job, 'endpoint': 'grpc.nvcf.nvidia.com:443',
                'function_id': function_id, 'model': args.model,
                'config': MessageToDict(config, preserving_proto_field_name=True),
                'wire_audio_format': 'raw PCM16' if args.raw_pcm else 'WAV container',
                'wire_audio_sha256': hashlib.sha256(raw).hexdigest(), 'wire_audio_bytes': len(raw),
                'request_sha256': hashlib.sha256(request.SerializeToString()).hexdigest(), 'attempts': 1}
            rate_limit()
            started = time.monotonic()
            try:
                response, rpc = service.stub.Recognize.with_call(request, timeout=90,
                    metadata=auth.get_auth_metadata(), wait_for_ready=False)
                row.update(grpc_status='OK', response=MessageToDict(response, preserving_proto_field_name=True))
                row['response_initial_metadata'] = {k: v for k, v in (rpc.initial_metadata() or [])
                    if any(word in k.lower() for word in ['request-id', 'requestid', 'nvcf'])}
            except grpc.RpcError as error:
                row.update(grpc_status=error.code().name, error=error.details().replace(key, '[REDACTED]')[:2000])
            row['seconds'] = round(time.monotonic() - started, 3)
            calls.append(row)
            out.write_text(json.dumps({'scope': 'NVIDIA offline ASR; model and function identified per call, not sound recognition',
                'manifest_sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'calls': calls}, indent=2) + '\n')
            text = ' '.join(r.get('alternatives', [{}])[0].get('transcript', '') for r in row.get('response', {}).get('results', []))
            print(job['case'], row['grpc_status'], repr(text), row.get('error', ''), flush=True)
            if row['grpc_status'] in ['UNAUTHENTICATED', 'PERMISSION_DENIED', 'NOT_FOUND', 'INVALID_ARGUMENT']:
                break
            if len(calls) >= 3 and all(c['grpc_status'] in ['RESOURCE_EXHAUSTED', 'UNAVAILABLE'] for c in calls[-3:]):
                break
    finally:
        auth.channel.close()


if __name__ == '__main__':
    main()
