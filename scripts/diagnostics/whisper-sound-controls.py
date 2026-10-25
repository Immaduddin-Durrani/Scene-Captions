"""Bounded offline trial of the cached Whisper sound-caption fine-tune. Never installs captions."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import time
import wave

ROOT = Path(__file__).resolve().parents[2]
REVISION = 'b815cffa35c2bc424d8acc07db50c3dd9430b978'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cases', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    report = args.report.resolve()
    if not report.is_relative_to((ROOT/'docs/verification').resolve()) or report.exists():
        parser.error('Choose a new report under docs/verification/.')
    snapshot = Path.home()/f'runtimes/cache/huggingface/hub/models--cahya--whisper-small-audio-captioning-v1.5/snapshots/{REVISION}'
    info = json.loads((Path.home()/'skill-library/setup-records/scenecaptions-whisper-captioning-2026-10-24.json').read_text())
    expected = next(item for item in info['siblings'] if item['rfilename']=='model.safetensors')
    with (snapshot/'model.safetensors').open('rb') as stream:
        actual = hashlib.file_digest(stream, 'sha256').hexdigest()
    if actual != expected['lfs']['sha256']:
        parser.error('Model weights do not match the pinned Hub object.')
    cases = json.loads(args.cases.read_text())
    if not 1 <= len(cases) <= 6: parser.error('At most six short local fixtures are permitted.')
    for case in cases:
        file = (ROOT/case['file']).resolve()
        if not file.is_relative_to((ROOT/'artifacts/sound-captions').resolve()): parser.error('Use local diagnostic inputs only.')
        if hashlib.sha256(file.read_bytes()).hexdigest() != case['sha256']: parser.error('Audio fixture hash changed.')
        with wave.open(str(file),'rb') as wav:
            duration = wav.getnframes()/wav.getframerate()
            if wav.getnchannels()!=1 or wav.getsampwidth()!=2 or wav.getframerate()!=16000 or not 0<duration<=8 or abs(duration-case['duration_s'])>1/16000:
                parser.error('Use actual short mono 16 kHz PCM fixtures with matching duration metadata.')
    os.environ['HF_HUB_OFFLINE']='1';os.environ['HF_HUB_DISABLE_TELEMETRY']='1'
    os.environ['HF_HOME']=str(Path.home()/'runtimes/cache/huggingface')
    import soundfile as sf
    import torch
    from transformers import WhisperProcessor, WhisperForConditionalGeneration
    torch.set_num_threads(4)
    processor=WhisperProcessor.from_pretrained(snapshot, local_files_only=True)
    model, loading=WhisperForConditionalGeneration.from_pretrained(snapshot,local_files_only=True,use_safetensors=True,output_loading_info=True)
    if any(loading.get(key) for key in ['missing_keys','unexpected_keys','mismatched_keys','error_msgs']):
        raise ValueError('Checkpoint weights do not fully match this runtime model; no inference accepted.')
    model.eval()
    device='mps' if torch.backends.mps.is_available() else 'cpu';model.to(device)
    result={'model':info['id'],'revision':REVISION,'weights_sha256':actual,'device':device,'weight_loading':loading,'max_new_tokens':96,'num_beams':3,'do_sample':False,'scope':'Small blind audio-description controls using the checkpoint generation defaults; no text labels passed to the model, full-film inference or playback installation.','generation_config':model.generation_config.to_dict(),'tests':[]}
    for case in cases:
        samples,rate=sf.read(ROOT/case['file'],dtype='float32');started=time.monotonic()
        inputs=processor(samples,sampling_rate=rate,return_tensors='pt',return_attention_mask=True)
        features=inputs.input_features.to(device)
        attention_mask=inputs.attention_mask.to(device)
        with torch.inference_mode(): generated=model.generate(features,attention_mask=attention_mask,max_new_tokens=96,num_beams=3,do_sample=False,return_dict_in_generate=True)
        text=processor.batch_decode(generated.sequences,skip_special_tokens=True)[0].strip()
        result['tests'].append({**case,'response':text,'generated_sequence_length':int(generated.sequences.shape[-1]),'seconds':round(time.monotonic()-started,3)})
        report.parent.mkdir(parents=True,exist_ok=True);report.write_text(json.dumps(result,indent=2)+'\n')
        print(case['name'],repr(text),flush=True)

if __name__=='__main__':main()
