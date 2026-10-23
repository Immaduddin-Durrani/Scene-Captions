"""Offline AudioSet inference, not an agent or an online captioning service."""
from pathlib import Path
import os,json,subprocess,time,hashlib
os.environ.setdefault('HF_HOME',str(Path.home()/'runtimes/cache/huggingface'))
os.environ.setdefault('HF_HUB_DISABLE_TELEMETRY','1')
os.environ.setdefault('HF_HUB_DISABLE_XET','1')
import torch,numpy as np,soundfile as sf
from transformers import AutoFeatureExtractor,AutoModelForAudioClassification
root=Path(__file__).resolve().parents[1]
cache=Path(os.environ.get('SCENECAPTIONS_AUDIO_CACHE',str(Path.home()/'runtimes/cache/scenecaptions-audio')));cache.mkdir(parents=True,exist_ok=True)
model_id='MIT/ast-finetuned-audioset-10-10-0.4593'
info=json.loads((cache/'model-info.json').read_text());revision=info['sha']
audio_path=cache/'bunny-16k.wav'
if not audio_path.exists():subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-i',str(root/'public/media/big-buck-bunny.mp4'),'-vn','-ac','1','-ar','16000',str(audio_path)],check=True)
print('Loading pinned classifier',revision,flush=True)
extractor=AutoFeatureExtractor.from_pretrained(model_id,revision=revision)
model=AutoModelForAudioClassification.from_pretrained(model_id,revision=revision,use_safetensors=True,attn_implementation='sdpa').eval()
device='mps' if torch.backends.mps.is_available() else 'cpu';torch.set_num_threads(4);model.to(device)
audio,sr=sf.read(audio_path,dtype='float32');duration=len(audio)/sr
window=10.;stride=2.;records=[]
starts=list(np.arange(0,duration-1,stride))
print(f'Analyzing {duration:.2f}s on {device}: {len(starts)} actual-audio windows',flush=True)
for offset in range(0,len(starts),4):
 batch=starts[offset:offset+4];arrays=[audio[int(s*sr):min(len(audio),int((s+window)*sr))] for s in batch]
 features=extractor(arrays,sampling_rate=sr,return_tensors='pt')
 with torch.inference_mode():scores=torch.sigmoid(model(**{k:v.to(device) for k,v in features.items()}).logits).cpu().numpy()
 for start,arr,values in zip(batch,arrays,scores):
  top=values.argsort()[-12:][::-1];records.append({'start_s':round(float(start),3),'end_s':round(min(float(start+window),duration),3),'rms':round(float(np.sqrt(np.mean(arr**2))),6),'predictions':[{'label':model.config.id2label[int(i)],'score':round(float(values[i]),6)} for i in top]})
 if offset%40==0:print(f'{min(offset+4,len(starts))}/{len(starts)} windows analyzed',flush=True)
result={'model':model_id,'revision':revision,'license':'BSD-3-Clause (model card)','window_seconds':window,'stride_seconds':stride,'audio_duration_seconds':duration,'video_sha256':hashlib.sha256((root/'public/media/big-buck-bunny.mp4').read_bytes()).hexdigest(),'method':'Actual 16 kHz mono soundtrack; multi-label sigmoid scores. Scores are uncalibrated model scores, not verified event probabilities. Timing is window-level, not forced alignment.','device':device,'windows':records}
(root/'docs/verification/sound-event-detections.json').write_text(json.dumps(result,indent=2)+'\n')
print('Saved all window predictions; no captions installed yet.',flush=True)
