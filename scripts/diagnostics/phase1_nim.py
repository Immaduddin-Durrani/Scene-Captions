"""Bounded NVIDIA-only, exact-payload experiments. No playback installation or paid provider."""
import argparse,base64,copy,hashlib,json,sys,time,urllib.request,urllib.error,wave,subprocess
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from nim_client import ROOT,api_key,rate_limit
ENDPOINT='https://integrate.api.nvidia.com/v1/chat/completions'
PHI_ENDPOINT='https://integrate.api.nvidia.com/v1/microsoft/phi-4-multimodal-instruct'

def audio_part(path, wire_type='audio_url'):
 path=Path(path).resolve();raw=path.read_bytes()
 with wave.open(str(path),'rb') as wav:
  duration=wav.getnframes()/wav.getframerate()
  if wav.getnchannels()!=1 or wav.getsampwidth()!=2 or wav.getframerate()!=16000 or not 0<duration<=30:raise ValueError('Use bounded mono 16-kHz PCM16 WAV fixtures')
 encoded=base64.b64encode(raw).decode()
 if wire_type not in ['audio_url','input_audio']:raise ValueError('Unsupported audio wire type')
 part={'type':'input_audio','input_audio':{'data':encoded,'format':'wav'}} if wire_type=='input_audio' else {'type':'audio_url','audio_url':{'url':'data:audio/wav;base64,'+encoded}}
 return part,{'file':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(raw).hexdigest(),'duration_s':duration,'sample_rate':16000,'channels':1,'sample_width':2,'wire_type':wire_type}

def video_part(path):
 path=Path(path).resolve();raw=path.read_bytes()
 if len(raw)>4*1024**2:raise ValueError('Diagnostic video exceeds 4 MB')
 info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(path)]))
 if not 0<float(info['format']['duration'])<=15:raise ValueError('Use <=15-second diagnostic video')
 return {'type':'video_url','video_url':{'url':'data:video/mp4;base64,'+base64.b64encode(raw).decode()}},{'file':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(raw).hexdigest(),'duration_s':float(info['format']['duration']),'bytes':len(raw),'streams':[{key:x.get(key) for key in ['codec_type','codec_name','width','height','sample_rate','channels']} for x in info['streams']]}

def image_part(path):
 path=Path(path).resolve();raw=path.read_bytes()
 if not raw.startswith(b'\xff\xd8\xff') or len(raw)>750_000:raise ValueError('Use bounded JPEG film frames')
 return {'type':'image_url','image_url':{'url':'data:image/jpeg;base64,'+base64.b64encode(raw).decode()}},{'file':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'modality':'image'}

def summarize(payload):
 out=copy.deepcopy(payload)
 for message in out.get('messages',[]):
  if not isinstance(message.get('content'),list):continue
  for part in message['content']:
   if 'input_audio' in part:
    raw=part['input_audio']['data'];part['input_audio']['data']={'base64_sha256':hashlib.sha256(raw.encode()).hexdigest(),'characters':len(raw)}
   for key in ['audio_url','video_url','image_url']:
    if key in part and part[key].get('url','').startswith('data:'):
     raw=part[key]['url'];part[key]['url']={'inline_media_sha256':hashlib.sha256(raw.encode()).hexdigest(),'data_uri_characters':len(raw),'prefix':raw.split(',',1)[0]}
 return out

def run_one(payload):
 key=api_key();rate_limit();wire=json.dumps(payload).encode();started=time.monotonic()
 endpoint=PHI_ENDPOINT if payload.get('model')=='microsoft/phi-4-multimodal-instruct' else ENDPOINT
 req=urllib.request.Request(endpoint,data=wire,headers={'Authorization':'Bearer '+key,'Content-Type':'application/json','Accept':'application/json'})
 row={'endpoint':endpoint,'payload':summarize(payload),'wire_sha256':hashlib.sha256(wire).hexdigest(),'wire_bytes':len(wire),'attempts':1}
 try:
  with urllib.request.urlopen(req,timeout=180) as r:
   row['http_status']=r.status;row['response_headers']={k:v for k,v in r.headers.items() if k.lower() in ['server','x-powered-by'] or any(x in k.lower() for x in ['request-id','requestid','ratelimit','retry-after','nvcf','nim-version','vllm-version'])};raw=r.read().decode()
   row['response']=json.loads(raw)
 except urllib.error.HTTPError as e:
  row['http_status']=e.code;row['error']=e.read().decode()[:2000].replace(key,'[REDACTED]')
 except (urllib.error.URLError,TimeoutError,ValueError) as e:row['error']=str(e).replace(key,'[REDACTED]');row['classification']='inconclusive-transport-or-response'
 row['seconds']=round(time.monotonic()-started,3)
 return row

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--manifest',type=Path,required=True);p.add_argument('--report',type=Path,required=True);p.add_argument('--max-calls',type=int,default=6);args=p.parse_args()
 out=args.report.resolve()
 if not out.is_relative_to((ROOT/'docs/verification').resolve()) or out.exists():p.error('Use a NEW verification report')
 jobs=json.loads(args.manifest.read_text())
 if not 1<=len(jobs)<=min(args.max_calls,12):p.error('At most twelve explicit bounded jobs per run')
 rows=[]
 for job in jobs:
  payload=copy.deepcopy(job['payload']);fixtures=[]
  for message in payload.get('messages',[]):
   if not isinstance(message.get('content'),list):continue
   for i,part in enumerate(message['content']):
    if part.get('type') in ['local_wav','local_mp4','local_jpeg']:
     if part['type']=='local_wav':converted,meta=audio_part(ROOT/part['path'],part.get('wire_type','audio_url'))
     elif part['type']=='local_mp4':converted,meta=video_part(ROOT/part['path'])
     else:converted,meta=image_part(ROOT/part['path'])
     message['content'][i]=converted;fixtures.append(meta)
  row={'case':job['case'],'hypothesis':job['hypothesis'],'fixtures':fixtures,**run_one(payload)};rows.append(row)
  out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps({'scope':'NVIDIA trial endpoint; single-attempt exact-payload controls; no auto acceptance, paid provider or installation','manifest_sha256':hashlib.sha256(args.manifest.read_bytes()).hexdigest(),'calls':rows},indent=2)+'\n')
  choice=(row.get('response',{}).get('choices') or [{}])[0]
  print(job['case'],row.get('http_status'),repr(choice.get('message',{}).get('content')),choice.get('finish_reason'),row.get('error',''),flush=True)

if __name__=='__main__':main()
