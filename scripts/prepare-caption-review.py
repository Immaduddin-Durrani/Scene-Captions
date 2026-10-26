"""Prepare contextual listening clips and a pending human-review receipt, without model calls."""
import argparse, hashlib, html, json, subprocess
from pathlib import Path
from nim_client import ROOT
from generation.review import review_receipt, validate_review


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--video', type=Path, required=True)
    parser.add_argument('--output-directory', type=Path)
    parser.add_argument('--rights-clear', action='store_true')
    parser.add_argument('--limit', type=int, default=3, help='Small packet by default; 0 includes all cues without any model calls')
    parser.add_argument('--check', type=Path, help='Check a completed human receipt instead of creating a packet')
    args = parser.parse_args()
    if not args.rights_clear or args.limit < 0:
        parser.error('Confirm rights-clear nonparticipant material and a nonnegative limit.')
    subprocess.run(['node', '--experimental-strip-types', str(ROOT/'scripts/validate-captions.ts'), str(args.input.resolve())], cwd=ROOT, check=True)
    raw = args.input.read_bytes(); track = json.loads(raw)
    caption_hash = hashlib.sha256(raw).hexdigest(); video_hash = hashlib.sha256(args.video.read_bytes()).hexdigest()
    if track['generated_with'].get('source_sha256') != video_hash:
        parser.error('Video bytes must match the caption track exact-edit hash.')
    if args.check:
        print(json.dumps(validate_review(track, caption_hash, video_hash, json.loads(args.check.read_text())), indent=2)); return
    if not args.output_directory:
        parser.error('Provide --output-directory for a new local review packet.')
    directory = args.output_directory.resolve()
    if not directory.is_relative_to((ROOT/'artifacts/caption-review').resolve()) or directory.exists():
        parser.error('Choose a NEW directory under artifacts/caption-review/.')
    directory.mkdir(parents=True)
    selected = track['cues'][:args.limit] if args.limit else track['cues']
    panels = []; clips = []
    for cue in selected:
        # Include context instead of assuming a subsecond caption interval captures the full event.
        start = max(0, cue['start_s']-1); end = min(track['duration_seconds'], cue['end_s']+1)
        filename = cue_digest_name(cue) + '.wav'
        subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-ss',str(start),'-i',str(args.video.resolve()),'-t',str(end-start),'-vn','-ac','1','-ar','16000','-y',str(directory/filename)],check=True)
        clips.append({'cue_id':cue['cue_id'],'file':filename,'clip_start_s':start,'clip_end_s':end,'source_interval_in_clip':[cue['start_s']-start,cue['end_s']-start]})
        variants = ''.join('<dt>'+html.escape(key)+'</dt><dd>'+html.escape(text)+'</dd>' for key,text in cue['grid'].items())
        reference = ('<h3>Licensed reference</h3><pre>'+html.escape(cue['reference_text'])+'</pre><h3>Generated fixed draft</h3>') if cue.get('reference_text') else '<h3>Fixed source caption</h3>'
        panels.append(f'<section><h2>{html.escape(cue["cue_id"])}</h2><p>Source interval {cue["start_s"]:.3f}–{cue["end_s"]:.3f}s. Local clip starts {start:.3f}s into the film.</p><audio controls preload="none" src="{filename}"></audio><details><summary>Compare reference, fixed caption and variants after listening</summary>{reference}<pre>{html.escape(cue["original_text"])}</pre><dl>{variants}</dl></details></section>')
    receipt = review_receipt(track, caption_hash, video_hash, selected)
    (directory/'review.json').write_text(json.dumps(receipt,indent=2)+'\n')
    (directory/'clips.json').write_text(json.dumps(clips,indent=2)+'\n')
    (directory/'index.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><title>Local caption listening review</title><style>body{font:18px/1.5 system-ui;max-width:850px;margin:2rem auto;padding:1rem}section{border-top:1px solid;padding:1rem 0}pre,dd{white-space:pre-wrap}audio{width:100%}</style><h1>Local caption review</h1><p>Listen first, then reveal source text. Review actual events, timing, all simultaneous sounds, every variant and reading time. Edit review.json with your reviewer ID and decisions: pending, approved, or needs-changes. All fields begin pending. Partial packets cannot approve a whole track. This tool neither installs captions nor certifies their correctness.</p>'+''.join(panels)+'</html>')
    print(f'Prepared {len(selected)}/{len(track["cues"])} cues in {directory.relative_to(ROOT)}. All decisions pending; no model calls or playback changes.')


def cue_digest_name(cue):
    from generation.review import cue_digest
    return cue_digest(cue)[:20]

if __name__ == '__main__':
    main()
