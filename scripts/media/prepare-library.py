"""Explicit offline preparation of the two official 720p films; never runs during viewing."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[2]
TITLES = {
    'sintel': {'title': 'Sintel', 'url': 'https://download.blender.org/durian/movies/Sintel.2010.720p.mkv.zip', 'bytes': 681285470, 'extension': 'zip', 'credit': '© 2010 Blender Foundation / durian.blender.org', 'about': 'https://durian.blender.org/about/'},
    'tears-of-steel': {'title': 'Tears of Steel', 'url': 'https://download.blender.org/demo/movies/ToS/tears_of_steel_720p.mov', 'bytes': 372178639, 'extension': 'mov', 'credit': '© 2012 Blender Foundation / mango.blender.org', 'about': 'https://mango.blender.org/about/'},
}


def digest(path):
    with path.open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()


def probe(path):
    return json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_format', '-show_streams', '-of', 'json', str(path)]))


def download(url, path, expected_bytes=None):
    if not path.exists():
        partial = path.with_name(path.name + '.partial')
        # A completed staged download is reusable; incomplete files are replaced.
        if expected_bytes is None or not partial.exists() or partial.stat().st_size != expected_bytes:
            print('Downloading', url, flush=True)
            with urllib.request.urlopen(url, timeout=60) as response, partial.open('wb') as output:
                shutil.copyfileobj(response, output)
        if expected_bytes is not None and partial.stat().st_size != expected_bytes:
            raise ValueError('Download size differs from the pinned official source.')
        partial.replace(path)
    if expected_bytes is not None and path.stat().st_size != expected_bytes:
        raise ValueError('Cached source size differs; inspect it rather than accepting it.')


def ffmpeg(*args):
    subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', *map(str, args)], check=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--film', choices=[*TITLES, 'all'], default='all')
    args = parser.parse_args()
    for executable in ['ffmpeg', 'ffprobe']:
        if not shutil.which(executable):
            parser.error(f'{executable} is required; no automatic installation.')
    cache = ROOT/'.media-cache/library'; media = ROOT/'public/media'; sources = ROOT/'data/sources/library'
    for directory in [cache, media, sources]: directory.mkdir(parents=True, exist_ok=True)
    for identity, film in TITLES.items():
        if args.film not in ['all', identity]: continue
        original = cache/(identity+'.'+film['extension'])
        download(film['url'], original, film['bytes'])
        source = original
        if film['extension'] == 'zip':
            source = cache/'sintel-source.mkv'
            if not source.exists():
                with zipfile.ZipFile(original) as archive:
                    entries = [item for item in archive.infolist() if item.filename.lower().endswith('.mkv')]
                    if len(entries) != 1: raise ValueError('Expected exactly one MKV film.')
                    staged = source.with_suffix('.partial')
                    with archive.open(entries[0]) as input_file, staged.open('wb') as output: shutil.copyfileobj(input_file, output)
                    staged.replace(source)
        info = probe(source); video = next(item for item in info['streams'] if item['codec_type'] == 'video')
        audio = next(item for item in info['streams'] if item['codec_type'] == 'audio')
        duration = float(info['format']['duration'])
        if not 0 < duration <= 1800: raise ValueError('Unexpected duration; nothing will be trimmed.')
        output = media/(identity+'.mp4'); record_file = media/(identity+'.resources.json')
        reusable = False
        if output.exists() and record_file.exists():
            old = json.loads(record_file.read_text()); reusable = old.get('sha256') == digest(output)
        if not reusable:
            staged = cache/(identity+'-browser.mp4')
            codec = ['-c:v', 'copy'] if video['codec_name'] == 'h264' and video.get('pix_fmt') == 'yuv420p' else ['-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p']
            ffmpeg('-i', source, '-map', '0:v:0', '-map', '0:a:0', *codec, '-c:a', 'aac', '-b:a', '128k', '-ac', '2', '-movflags', '+faststart', staged)
            prepared = probe(staged); streams = prepared['streams']; result_video = next(s for s in streams if s['codec_type'] == 'video')
            if (result_video['width'], result_video['height']) != (video['width'], video['height']) or abs(float(prepared['format']['duration'])-duration) > 1:
                raise ValueError('Browser copy failed dimensions/duration verification.')
            if not any(s['codec_type'] == 'audio' and s['codec_name'] == 'aac' for s in streams): raise ValueError('AAC audio is missing.')
            staged.replace(output)
        final = probe(output)
        ffmpeg('-ss', '60', '-i', output, '-frames:v', '1', '-update', '1', media/(identity+'-poster.jpg'))
        srt = sources/(identity+'-en.srt')
        subtitle_source = None
        if identity == 'tears-of-steel':
            subtitle_source = 'https://download.blender.org/demo/movies/ToS/subtitles/TOS-en.srt'
            download(subtitle_source, srt, 4764)
        else:
            english = [s for s in info['streams'] if s['codec_type'] == 'subtitle' and s.get('tags', {}).get('language', '').lower() in ['eng', 'en']]
            if english:
                subtitle_source = 'English subtitle stream embedded in official Sintel 720p MKV'
                ffmpeg('-i', source, '-map', '0:'+str(english[0]['index']), '-c:s', 'srt', srt)
        if not subtitle_source: raise ValueError('No confirmed English subtitle source; do not guess a language.')
        ffmpeg('-i', srt, media/(identity+'-en.vtt'))
        record = {'id': identity, 'title': film['title'], 'durationSeconds': float(final['format']['duration']), 'video': '/media/'+identity+'.mp4', 'poster': '/media/'+identity+'-poster.jpg', 'englishSubtitles': '/media/'+identity+'-en.vtt', 'subtitleSource': subtitle_source, 'subtitleTimingReviewed': False, 'nonSpeechCaptionStatus': 'not-prepared', 'source': film['url'], 'sourceSha256': digest(source), 'credit': film['credit'], 'license': 'CC BY 3.0', 'licenseSource': film['about'], 'modifications': 'Full 720p-release picture/credits retained; MP4 remux with original H.264 video where compatible, stereo AAC audio and extracted poster/subtitles', 'sha256': digest(output), 'bytes': output.stat().st_size, 'streams': [{'codec_type': s['codec_type'], 'codec_name': s['codec_name'], **({k: s[k] for k in ['width', 'height']} if s['codec_type']=='video' else {})} for s in final['streams']]}
        record_file.write_text(json.dumps(record, indent=2)+'\n')
        (sources/(identity+'.resources.json')).write_text(json.dumps(record, indent=2)+'\n')
        print(f"Ready: {identity}, {record['durationSeconds']:.3f}s. Sound-caption coverage not certified.", flush=True)


if __name__ == '__main__': main()
