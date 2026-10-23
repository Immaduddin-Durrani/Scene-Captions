"""Local-only NVIDIA client. Never import into the web application."""
from pathlib import Path
import os,json,time,urllib.request,urllib.error,threading
ROOT=Path(__file__).resolve().parents[1]
MODEL='nvidia/nemotron-3-nano-omni-30b-a3b-reasoning'
_last_request=0.
_rate_lock=threading.Lock()
def api_key():
    value=os.environ.get('NVIDIA_API_KEY','')
    file=ROOT/'.env'
    if file.exists():
        for line in file.read_text().splitlines():
            name,sep,text=line.strip().removeprefix('export ').partition('=')
            if sep and name.strip()=='NVIDIA_API_KEY':value=text.strip().strip('\"\'')
    if not value:raise RuntimeError('NVIDIA_API_KEY is missing. Set it in local .env.')
    return value

def request(content,max_tokens=4096,thinking=True):
    global _last_request
    key=api_key()
    payload={'model':MODEL,'messages':[{'role':'user','content':content}],'max_tokens':max_tokens,'temperature':0.2,'stream':False,'chat_template_kwargs':{'enable_thinking':thinking}}
    if thinking:payload['reasoning_budget']=512
    for attempt in range(3):
        with _rate_lock:
            delay=2.05-(time.monotonic()-_last_request)
            if delay>0:time.sleep(delay)
            _last_request=time.monotonic()
        req=urllib.request.Request('https://integrate.api.nvidia.com/v1/chat/completions',data=json.dumps(payload).encode(),headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'})
        try:
            with urllib.request.urlopen(req,timeout=180) as response:return json.load(response)
        except urllib.error.HTTPError as error:
            if error.code in [429,502,503,504] and attempt<2:time.sleep(2**(attempt+1));continue
            message=error.read().decode()[:1200].replace(key,'[REDACTED]')
            raise RuntimeError(f'NVIDIA HTTP {error.code}: {message}') from None

def parse_json(response):
    text=response['choices'][0]['message'].get('content','').strip()
    if text.startswith('```'):text=text.split('\n',1)[1].rsplit('```',1)[0]
    return json.loads(text)
