"""Prepare bounded BBB reference/visual-context jobs, without inference or installation."""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROMPT_VERSION = 'bbb-nim-reference-visual-v3'
PROMPT = '''Draft non-speech captions for Deaf and hard-of-hearing viewers.
The supplied video has NO AUDIO. The licensed reference is the only SOUND evidence.
Use pixels ONLY to identify the visible source/action associated with the reference
event at the target interval. Plot context: a large rabbit is bullied by forest
creatures and eventually fights back (Blender Studio official synopsis). Plot is
not evidence of a particular event or sound. Do not use remembered film details.

Produce three meaningful levels: Essential names every sound briefly (<=40 chars);
Balanced identifies its supported source and sound action (<=72 chars); Detailed
adds relevant, actually visible source/action/context (<=100 chars). Do not expand
merely with punctuation, redundant words or scenic filler. Music adjectives may
come from the reference; instruments, rhythm, pitch and intensity need actual
audio evidence, which is unavailable. Never invent them. If evidence is too thin,
levels may be identical: explain this in limitation. More detail is not inherently
better. Avoid subjective narrative, emotions, intentions, spoilers and unnecessary
color descriptions. Preserve ALL concurrent reference events at ALL levels.

Visible location/action is allowed: reference [DOOR CREAKS] + visible door opening
can yield [Creaking], [A door creaks], [The door creaks as it opens]. This is a
reference-assisted transformation, not independent audio recognition.
Caption ONLY the target interval. Surrounding seconds give context, not extra
events to caption. Keep each caption in square brackets, with separate lines for
simultaneous sounds. Return JSON, no markdown, with exactly these keys:
cue_id, visual_facts (array of concise strings), sound_facts (array of reference
events), essential (string), balanced (string), detailed (string), added_details
(array of objects with detail and basis), limitation (string).
'''


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--ids', required=True, help='Comma-separated one-based source indices, at most 12')
    p.add_argument('--manifest', type=Path, required=True)
    args = p.parse_args()
    ids = [int(x) for x in args.ids.split(',')]
    if not 1 <= len(ids) <= 12 or len(set(ids)) != len(ids) or any(x < 1 or x > 87 for x in ids):
        p.error('Use 1–12 distinct source indices in 1–87')
    out = args.manifest.resolve()
    artifacts = ROOT / 'artifacts/nim-phase1-2026-10-26'
    if not out.is_relative_to(artifacts) or out.exists():
        p.error('Use a NEW manifest under this task artifacts directory')
    video = ROOT / 'public/media/big-buck-bunny.mp4'
    source = json.loads((ROOT / 'data/sources/big-buck-captions/generation-reference.json').read_text())
    if hashlib.sha256(video.read_bytes()).hexdigest() != source['generated_with']['source_sha256']:
        p.error('Exact video edit hash differs')
    reference = ROOT / 'data/sources/big-buck-captions/big-buck-bunny.srt'
    if hashlib.sha256(reference.read_bytes()).hexdigest() != source['generated_with']['caption_source']['sha256']:
        p.error('Reference SRT hash differs')
    directory = artifacts / 'context-clips'
    directory.mkdir(parents=True, exist_ok=True)
    jobs = []
    for index in ids:
        cue = source['cues'][index - 1]
        start = max(0, cue['start_s'] - 5)
        end = min(596.461678, cue['end_s'] + 5)
        # Seven-second final music cue exceeds the 15s diagnostic cap: trim context
        # symmetrically, preserving the entire original target interval.
        excess = max(0, end - start - 15)
        start += excess / 2
        end -= excess / 2
        path = directory / (cue['cue_id'] + '.mp4')
        # Deterministic local extraction; no model or external service.
        if not path.exists():
            subprocess.run(['ffmpeg','-v','error','-ss',str(start),'-i',str(video),
                '-t',str(end-start),'-an','-vf','scale=512:-2,fps=2','-c:v',
                'libx264','-crf','25','-movflags','+faststart',str(path)], check=True)
        context = {'cue_id':cue['cue_id'],'reference_caption':cue['original_text'],
            'target_interval_in_clip':[round(cue['start_s']-start,3),round(cue['end_s']-start,3)],
            'clip_start_in_film_s':start,'reference_source':source['generated_with']['caption_source']['url']}
        jobs.append({'case':cue['cue_id']+'-v3','prompt_version':PROMPT_VERSION,
            'hypothesis':'Source events plus silent visual context can support useful detail without inventing acoustic attributes; draft only, not listening approval.',
            'source_context':context,'payload':{'model':'nvidia/nemotron-3.5-super-vl-120b-a12b',
                'messages':[{'role':'user','content':[{'type':'text','text':PROMPT+'\n'+json.dumps(context)},
                    {'type':'local_mp4','path':str(path.relative_to(ROOT))}]}],
                'reasoning_effort':'low','max_tokens':8192,'temperature':0.2,'stream':False}})
    out.write_text(json.dumps(jobs,indent=2)+'\n')
    print(f'Prepared {len(jobs)} silent clips and explicit NIM jobs. No inference or installation.')


if __name__ == '__main__':
    main()
