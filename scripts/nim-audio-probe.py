from pathlib import Path
import base64,json,sys
from nim_client import ROOT,request
cache=Path.home()/'runtimes/cache/scenecaptions-audio'
calibration='--calibration' in sys.argv
audio=cache/('calibration-beep.wav' if calibration else 'nvidia-audio-probe.wav')
question='Describe the audible sounds in this recording. Do not infer objects or setting. Be specific about whether there is music, speech, silence, or simple tones. If you cannot access the audio, say so. Return JSON {"description":"..."}.'
content=[{'type':'audio_url','audio_url':{'url':'data:audio/wav;base64,'+base64.b64encode(audio.read_bytes()).decode()}},{'type':'text','text':question}]
r=request(content,4096,thinking=True)
path=ROOT/'docs/verification'/('nim-calibration-probe.json' if calibration else 'nim-audio-url-probe.json')
path.write_text(json.dumps(r,indent=2)+'\n')
print('Usage:',r.get('usage'));print(r['choices'][0]['message'].get('content'))
