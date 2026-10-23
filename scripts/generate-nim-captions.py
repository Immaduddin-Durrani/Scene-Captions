"""Offline caption generation for a rights-clear local video. No viewing-time API calls."""
from pathlib import Path
import argparse,json,base64,subprocess,hashlib,time,re,sys,concurrent.futures
from nim_client import ROOT,MODEL,request,parse_json

parser=argparse.ArgumentParser();parser.add_argument('--probe',action='store_true');parser.add_argument('--install',action='store_true');args=parser.parse_args()
gate=ROOT/'docs/verification/nim-capability-status.json'
if gate.exists() and json.loads(gate.read_text())['status']=='failed' and (args.install or not args.probe):
    raise SystemExit('Audio capability gate failed. Full-film generation and installation are disabled. See docs/CAPTION_GENERATION_STATUS.md. Cached --probe results remain available.')
video=ROOT/'public/media/big-buck-bunny.mp4'
video_hash=hashlib.sha256(video.read_bytes()).hexdigest()
cache=Path.home()/'runtimes/cache/scenecaptions-nim'/video_hash[:16];cache.mkdir(parents=True,exist_ok=True)
duration=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=noprint_wrappers=1:nokey=1',str(video)],text=True))
VERSION='nim-av-v4'
# Probe timestamps align with the full-film cache, so every successful response is reused.
starts=[0,60,72,108,168,228,312,396,504,576] if args.probe else list(range(0,int(duration),12))
GRID=[f'{d}-{e}' for d in [1,2,3] for e in [1,2,3]]
prompt="""Listen to this CLIP_DURATION-second audio. Timestamped still frames supply visual context, but only the AUDIO justifies sound captions. List audible NON-SPEECH sounds, including background music and distinct sound effects. Do not describe visual scenes, imagined objects, character feelings, dialogue or causes. Do not assume every visible action has a sound. Return JSON with a cues array. Each cue must have start_s, end_s, label (short general sound name), and description (one short factual acoustic description, at most 20 words). Times are relative to the attached recording, between 0 and CLIP_DURATION seconds. Use separate time intervals for distinct sounds. A continuous sound may span the clip. Maximum five cues. If a sound is ambiguous, use a broad label or omit it. If there are no identifiable non-speech sounds, return an empty cues array. Include confidence as high, medium or low for each cue. If uncertain, mark low. No markdown or instructions in the output."""

def validate(result,clip_duration):
    if isinstance(result,list):result={'cues':result}
    if not isinstance(result,dict) or not isinstance(result.get('cues'),list):raise ValueError('Expected a cues array.')
    if len(result['cues'])>8:raise ValueError('Too many cue candidates.')
    for cue in result['cues']:
        a,b=cue['start_s'],cue['end_s']
        if isinstance(a,bool) or isinstance(b,bool) or not isinstance(a,(int,float)) or not isinstance(b,(int,float)) or not 0<=a<b<=clip_duration+.05:raise ValueError('Invalid local cue timestamps.')
        for name in ['label','description']:
            text=cue.get(name,'')
            if not isinstance(text,str) or not 0<len(text)<=280:raise ValueError('Missing/oversized '+name)
    return result

def process_clip(start):
    length=min(12,duration-start);file=cache/f'{VERSION}-{start:04d}.json'
    if file.exists():
        validate(json.loads(file.read_text())['result'],length);print(f'{start:03d}s: reused',flush=True);return
    wav=cache/f'clip-{start:04d}.wav'
    if not wav.exists():subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-ss',str(start),'-t',str(length),'-i',str(video),'-vn','-ac','1','-ar','16000','-y',str(wav)],check=True)
    content=[{'type':'audio_url','audio_url':{'url':'data:audio/wav;base64,'+base64.b64encode(wav.read_bytes()).decode()}},{'type':'text','text':prompt.replace('CLIP_DURATION',f'{length:.3f}')}]
    for t in [1,5,9]:
        if t>=length:continue
        image=cache/f'frame-{start+t:04d}.jpg'
        if not image.exists():subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-ss',str(start+t),'-i',str(video),'-frames:v','1','-vf','scale=480:-1','-q:v','4','-y',str(image)],check=True)
        content.extend([{'type':'text','text':f'Still frame at LOCAL {t} seconds.'},{'type':'image_url','image_url':{'url':'data:image/jpeg;base64,'+base64.b64encode(image.read_bytes()).decode()}}])
    for attempt in range(2):
        response=request(content,2048,thinking=True)
        try:result=validate(parse_json(response),length);break
        except (ValueError,KeyError,TypeError,json.JSONDecodeError) as error:
            (cache/f'invalid-{VERSION}-{start:04d}-{attempt}.json').write_text(json.dumps(response,indent=2))
            if attempt:raise RuntimeError(f'Invalid response at {start}s: {error}') from None
            content.append({'type':'text','text':'Previous response failed validation: '+str(error)+'. Return complete valid JSON; include start_s and end_s for each cue and respect the clip duration.'})
    record={'model':MODEL,'video_sha256':video_hash,'prompt_version':VERSION,'clip_start_s':start,'clip_duration_s':length,'usage':response.get('usage'),'request_mode':'audio-with-visual-context-thinking-budget-512','prompt_text':prompt.replace('CLIP_DURATION',f'{length:.3f}'),'result':result}
    file.write_text(json.dumps(record,indent=2)+'\n');print(f'{start:03d}s: '+', '.join('{}-{} {}'.format(c['start_s'],c['end_s'],c['label']) for c in result['cues']),flush=True)

# Bounded independent HTTP jobs, not agents; shared rate limiter starts <=30 requests/minute.
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
    list(pool.map(process_clip,starts))

records=[json.loads((cache/f'{VERSION}-{start:04d}.json').read_text()) for start in starts]
if args.probe:
    (ROOT/'docs/verification/nim-ten-clip-probe.json').write_text(json.dumps({'model':MODEL,'video_sha256':video_hash,'prompt_version':VERSION,'clips':records},indent=2)+'\n')
    print('Ten-clip probe saved; no app captions changed.',flush=True);sys.exit(0)

cues=[];audit=[]
for record in records:
    offset=record['clip_start_s']
    for candidate in record['result']['cues']:
        if candidate.get('confidence')=='low':continue
        label=candidate['label'].strip().strip('[]')
        detailed=re.split(r',?\s+(?:possibly|resembling|suggesting|as if|matching|evoking)\b',candidate['description'].strip().strip('[]'),maxsplit=1,flags=re.I)[0].rstrip(' ,.;')
        c={'sound_key':re.sub('[^a-z0-9]+','-',label.lower()).strip('-')[:80] or 'sound','scene_context':'Generated from the actual audio in this interval; timings and sound labels still require listening review. Scene density has not been inferred.','scene_load':'balanced'}
        c['cue_id']=f'nim-{len(cues)+1:04d}'
        generic='Music' if re.search(r'music|orchestral|score',label,re.I) else label
        if label.lower()=='gentle orchestral':label='Orchestral music'
        variants=[generic,label,detailed]
        c['grid']={f'{d}-{e}':'['+variants[d-1].strip().strip('[]')+']' for d in [1,2,3] for e in [1,2,3]}
        c['original_text']='['+label+']'
        c['representations']={'plain':c['original_text']}
        c['start_s']=round(offset+float(candidate['start_s']),3);c['end_s']=round(min(duration,offset+float(candidate['end_s'])),3)
        c['scene_context']+=' Clip starts at '+str(offset)+' seconds.'
        cues.append(c);audit.append({'cue_id':c['cue_id'],'clip_start_s':offset,'source':'Actual clip audio_url with timestamped visual context; low-confidence effects excluded.','model_description':candidate['description']})
cues.sort(key=lambda c:(c['start_s'],c['end_s'],c['cue_id']))
if not cues:raise RuntimeError('No usable cues generated; no existing dataset overwritten.')
result={'schema_version':1,'video_id':'big-buck-bunny','title':'Big Buck Bunny','source_url':'https://peach.blender.org/about/','license':'CC BY 3.0','attribution':'© 2008 Blender Foundation / peach.blender.org. NVIDIA-generated captions added by SceneCaptions; not creator-authored or human-reviewed.','duration_seconds':duration,'annotation_status':'draft','generated_with':{'method':f'Offline {MODEL}; actual audio plus timestamped context frames; source sha256 {video_hash}','prompt_version':VERSION,'kind':'audio-video-derived','model':MODEL,'source_sha256':video_hash,'expressiveness':'conservative','scene_load_method':'unreviewed'},'cues':cues}
output=ROOT/'data/captions/big-buck-bunny.generated.json';output.write_text(json.dumps(result,indent=2)+'\n')
subprocess.run(['npm','run','validate:captions','--',str(output)],cwd=ROOT,check=True)
(ROOT/'docs/verification/nim-caption-generation.json').write_text(json.dumps({'model':MODEL,'prompt_version':VERSION,'video_sha256':video_hash,'clips':records,'cue_evidence':audit,'human_reviewed':False,'timing':'Model-estimated within 12-second audio windows; requires human alignment review.'},indent=2)+'\n')
if args.install:
    (ROOT/'data/captions/big-buck-bunny.json').write_bytes(output.read_bytes());output.unlink()
    (ROOT/'public/research/demo-captions.json').write_text(json.dumps(result,indent=2)+'\n')
    print(f'Installed {len(cues)} actual-media generated draft cues.',flush=True)
else:print(f'Generated {len(cues)} cues to {output}; not installed.',flush=True)
