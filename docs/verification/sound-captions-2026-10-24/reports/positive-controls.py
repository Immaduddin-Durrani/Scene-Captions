import os,json
from pathlib import Path
os.environ['HF_HUB_OFFLINE']='1';os.environ['HF_HUB_DISABLE_TELEMETRY']='1'
from mlx_vlm import load,generate
from mlx_vlm.prompt_utils import apply_chat_template
model,processor=load('/Users/hamza/runtimes/cache/scenecaptions-gemma3n-66e7276',trust_remote_code=False)
cases=[('text-only','What is 2 + 3? Answer only the number.',None),('official-speech','Transcribe the speech in this audio.', 'artifacts/sound-captions/control-v1/078305bc50bc6bf2ea62.wav')]
rows=[]
for name,prompt,audio in cases:
 formatted=apply_chat_template(processor,model.config,prompt,num_audios=1 if audio else 0)
 r=generate(model,processor,formatted,audio=[audio] if audio else None,max_tokens=96,temperature=0.,verbose=False)
 rows.append({'name':name,'prompt':prompt,'audio':audio,'response':r.text,'generation_tokens':r.generation_tokens,'finish_reason':r.finish_reason,'cached_tokens':r.cached_tokens});print(name,repr(r.text),flush=True)
Path('docs/verification/sound-captions-2026-10-24/reports/positive-controls.json').write_text(json.dumps(rows,indent=2)+'\n')
