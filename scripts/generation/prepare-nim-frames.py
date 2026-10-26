"""Prepare source-assisted BBB jobs using only frames inside each source interval."""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VERSION = 'bbb-nim-exact-frames-v4'
MODEL = 'nvidia/nemotron-3.5-super-vl-120b-a12b'
PROMPT = '''Create three levels of non-speech captions for a DHH-centered research demo.
This is REFERENCE-ASSISTED generation: the supplied images are silent. Sound events
come ONLY from the licensed reference. Images identify relevant visible context;
they cannot prove acoustic properties. Each cue has two frames INSIDE its interval.
Never import actions/characters from memory, the plot, another cue, or another time.

For EACH numbered reference event produce:
essential: shortest understandable sound category/event;
balanced: the source and sound action, plus any salient reference attribute;
detailed: add relevant visible source/action/location if firmly supported by that
cue's images. Prefer helpful context (who/what/where) over redundant articles,
unnecessary color, decorative language, or scene narration. Do not describe
unrelated scenery. If no additional supported fact exists, repeat the balanced
caption and explain the limit; a richer label must not invent information.
Do not add instruments, loudness, pitch, rhythm, emotions or sound direction unless
the REFERENCE states them. A visible location is allowed. Reference [DOOR CREAKS]
plus a visible person opening it can become [Creaking], [A door creaks],
[The door creaks as it opens]. The opening is visible, the creak is reference-only.
Keep reference attributes such as pain/anger when appropriate for the detail level.
Unidentified sources stay unidentified. An off-screen source is not automatically
an inaudible one; do not drop its reference event because it is not pictured.

Return ALL cues and ALL reference events, in order. Each caption is ONE bracketed
line, with no internal newline. At most 40/65/95 characters per event, respectively.
Avoid repeated brackets and padding. Source intervals will not be extended: shorter
captions are preferable, especially for the subsecond intervals. Reading time still
needs separate review. Keep visual_facts factual and specific to that cue's images.
Each added_detail must cite reference or visible as its basis. No invented audio
observations. Empty visual facts and equal levels are allowed. Return only JSON.
'''

def schema():
    event = {'type':'object','additionalProperties':False,'properties':{
        'index':{'type':'integer'},
        **{k:{'type':'string'} for k in ['essential','balanced','detailed']},
        'added_details':{'type':'array','items':{'type':'object','additionalProperties':False,
            'properties':{'detail':{'type':'string'},'basis':{'type':'string','enum':['reference','visible']}},
            'required':['detail','basis']}},'limitation':{'type':'string'}},
        'required':['index','essential','balanced','detailed','added_details','limitation']}
    cue = {'type':'object','additionalProperties':False,'properties':{
        'cue_id':{'type':'string'},'visual_facts':{'type':'array','items':{'type':'string'}},
        'events':{'type':'array','items':event}},'required':['cue_id','visual_facts','events']}
    return {'type':'json_schema','json_schema':{'name':'source_assisted_captions','strict':True,
        'schema':{'type':'object','additionalProperties':False,'properties':{
            'cues':{'type':'array','items':cue}},'required':['cues']}}}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--ids',required=True,help='One-based source indices, comma-separated; maximum 36')
    p.add_argument('--manifest',type=Path,required=True)
    a=p.parse_args();ids=[int(x) for x in a.ids.split(',')]
    if not 1<=len(ids)<=36 or len(ids)!=len(set(ids)) or any(x<1 or x>87 for x in ids):p.error('Use 1–36 unique indices in 1–87')
    out=a.manifest.resolve();directory=ROOT/'artifacts/nim-only-2026-10-26'
    if out.exists() or not out.is_relative_to(directory):p.error('Use a NEW manifest under this task artifacts')
    source=json.loads((ROOT/'data/sources/big-buck-captions/generation-reference.json').read_text())
    film=ROOT/'public/media/big-buck-bunny.mp4'
    if hashlib.sha256(film.read_bytes()).hexdigest()!=source['generated_with']['source_sha256']:p.error('Film hash differs')
    reference=ROOT/'data/sources/big-buck-captions/big-buck-bunny.srt'
    if hashlib.sha256(reference.read_bytes()).hexdigest()!=source['generated_with']['caption_source']['sha256']:p.error('SRT hash differs')
    frames=directory/'frames';frames.mkdir(parents=True,exist_ok=True)
    jobs=[]
    for offset in range(0,len(ids),3):
        content=[{'type':'text','text':PROMPT}];contexts=[]
        for i in ids[offset:offset+3]:
            cue=source['cues'][i-1]
            times=[round(cue['start_s']+(cue['end_s']-cue['start_s'])*fraction,3) for fraction in [.25,.75]]
            context={'cue_id':cue['cue_id'],'start_s':cue['start_s'],'end_s':cue['end_s'],
                'events':[{'index':n+1,'reference':line} for n,line in enumerate(cue['original_text'].split('\n'))],
                'frame_times_s':times}
            contexts.append(context);content.append({'type':'text','text':json.dumps(context)})
            for t in times:
                # Film hash + exact extraction specification forms the cache key.
                key=hashlib.sha256(f'{source["generated_with"]["source_sha256"]}:{t}:512:q4'.encode()).hexdigest()[:20]
                path=frames/(key+'.jpg')
                if not path.exists():subprocess.run(['ffmpeg','-v','error','-ss',str(t),'-i',str(film),'-frames:v','1','-vf','scale=512:-2','-q:v','4',str(path)],check=True)
                content.extend([{'type':'text','text':f'{cue["cue_id"]} frame at {t}s (inside interval).'},
                    {'type':'local_jpeg','path':str(path.relative_to(ROOT))}])
        jobs.append({'case':'frames-'+ '-'.join(f'{i:03d}' for i in ids[offset:offset+3]),
            'hypothesis':'Exact-interval frames avoid importing surrounding actions; each reference event gets explicit evidence-bounded detail levels.',
            'prompt_version':VERSION,'source_context':contexts,'payload':{
                'model':MODEL,'messages':[{'role':'user','content':content}],
                'reasoning_effort':'none','temperature':0.2,'max_tokens':8192,'stream':False,
                'response_format':schema()}})
    out.write_text(json.dumps(jobs,indent=2)+'\n')
    print(f'Prepared {len(contexts) if len(jobs)==1 else len(ids)} source cues in {len(jobs)} bounded jobs; no inference or installation.')

if __name__=='__main__':main()
