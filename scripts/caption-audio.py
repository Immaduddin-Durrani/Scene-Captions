"""Generate actual-audio descriptions locally; never invoked by the player."""
from pathlib import Path
import os,json,time,sys
os.environ.setdefault('HF_HOME',str(Path.home()/'runtimes/cache/huggingface'))
os.environ.setdefault('HF_HUB_DISABLE_TELEMETRY','1')
os.environ.setdefault('HF_HUB_DISABLE_XET','1')
import torch,soundfile as sf
from transformers import WhisperProcessor,WhisperForConditionalGeneration
root=Path(__file__).resolve().parents[1];cache=Path.home()/'runtimes/cache/scenecaptions-audio'
info=json.loads((cache/'caption-model-info.json').read_text());model_id=info['id'];revision=info['sha']
print('Loading audio captioning model',model_id,revision,flush=True)
processor=WhisperProcessor.from_pretrained(model_id,revision=revision)
model=WhisperForConditionalGeneration.from_pretrained(model_id,revision=revision,use_safetensors=True).eval()
device='mps' if torch.backends.mps.is_available() else 'cpu';model.to(device);torch.set_num_threads(4)
audio,sr=sf.read(cache/'bunny-16k.wav',dtype='float32')
starts=[2,74,300,580] if '--probe' in sys.argv else list(range(0,int(len(audio)/sr),8))
path=root/'docs/verification/audio-caption-probe.json' if '--probe' in sys.argv else root/'docs/verification/audio-caption-descriptions.json'
records=json.loads(path.read_text()).get('windows',[]) if path.exists() else []
for start in starts:
 if any(x['start_s']==start for x in records):continue
 stop=min(start+8,len(audio)/sr)
 features=processor(audio[start*sr:int(stop*sr)],sampling_rate=sr,return_tensors='pt').input_features.to(device)
 with torch.inference_mode():
  output=model.generate(features,max_new_tokens=80,num_beams=3,do_sample=False,language='en',task='transcribe',return_timestamps=False)
 description=processor.batch_decode(output,skip_special_tokens=True)[0].strip()
 records.append({'start_s':start,'end_s':round(stop,3),'description':description})
 path.write_text(json.dumps({'model':model_id,'revision':revision,'license':'Apache-2.0 (model card)','method':'Local audio-captioning fine-tune, actual 8-second soundtrack windows; not human reviewed or exact event alignment.','windows':records},indent=2)+'\n')
 print(start,description,flush=True)
