import os,json,hashlib
from pathlib import Path
os.environ['HF_HUB_OFFLINE']='1';os.environ['HF_HUB_DISABLE_TELEMETRY']='1'
import mlx.core as mx
from mlx_vlm import load
from mlx_vlm.prompt_utils import apply_chat_template
from mlx_vlm.utils import prepare_inputs
p=Path('/Users/hamza/runtimes/cache/scenecaptions-gemma3n-66e7276')
model,processor=load(str(p),trust_remote_code=False)
prompt=apply_chat_template(processor,model.config,'Describe only the audible contents of this recording.',num_audios=1)
rows=[]
for case in json.loads(Path('artifacts/sound-captions/control-v1/cases.json').read_text()):
 inputs=prepare_inputs(processor,images=None,audio=[case['file']],prompts=prompt)
 rows.append({'name':case['name'],'processor':type(processor).__name__,'feature_extractor':type(processor.feature_extractor).__name__,'prompt':prompt,'audio_token_id':processor.audio_token_id,'inputs':{k:{'shape':list(v.shape),'dtype':str(v.dtype),'min':float(mx.min(v).item()),'max':float(mx.max(v).item()),'sha256':hashlib.sha256(memoryview(v).tobytes()).hexdigest()} for k,v in inputs.items() if isinstance(v,mx.array)},'audio_token_count':int(mx.sum(inputs['input_ids']==processor.audio_token_id).item())})
Path('docs/verification/sound-captions-2026-10-24/reports/input-inspection.json').write_text(json.dumps(rows,indent=2)+'\n');print([(r['name'],r['audio_token_count'],r['inputs']) for r in rows])
