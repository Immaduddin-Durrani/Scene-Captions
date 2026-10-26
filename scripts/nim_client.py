"""Local-only NVIDIA client. Never import into the web application."""
from pathlib import Path
import os,json,time,urllib.request,urllib.error,threading
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone
from contextlib import contextmanager
ROOT=Path(__file__).resolve().parents[1]
MODEL='nvidia/nemotron-3-nano-omni-30b-a3b-reasoning'
_rate_lock=threading.Lock()
MIN_REQUEST_INTERVAL = 2.05  # About 29 starts/minute, below the user-specified 40 RPM.
MAX_ATTEMPTS = 7
MAX_BACKOFF = 60
TEXT_TIMEOUT = 180
REASONING_TIMEOUT = 300


@contextmanager
def _process_lock(handle):
    handle.seek(0)
    if os.name == 'nt':
        import msvcrt
        msvcrt.locking(handle.fileno(), msvcrt.LK_LOCK, 1)
    else:
        import fcntl
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
    try:
        yield
    finally:
        handle.seek(0)
        if os.name == 'nt':
            msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def rate_limit():
    """Coordinate request starts across threads and local project processes."""
    directory = ROOT / 'artifacts/nim-rate-limit'
    directory.mkdir(parents=True, exist_ok=True)
    with _rate_lock, (directory / 'requests.lock').open('a+b') as handle:
        if handle.seek(0, 2) == 0:
            handle.write(b'0'); handle.flush()
        with _process_lock(handle):
            handle.seek(0)
            try:
                last = float(handle.read().decode())
            except ValueError:
                last = 0
            now = time.time()
            # Recover safely from a clock adjustment; never wait hours for a stale timestamp.
            delay = min(MIN_REQUEST_INTERVAL, max(0, last + MIN_REQUEST_INTERVAL - now))
            if delay:
                time.sleep(delay)
            handle.seek(0); handle.truncate()
            handle.write(str(time.time()).encode()); handle.flush()


def _retry_delay(attempt, retry_after=None):
    delay = min(MAX_BACKOFF, 2 ** (attempt + 1))
    if retry_after:
        try:
            advised = float(retry_after)
        except ValueError:
            try:
                advised = (parsedate_to_datetime(retry_after) - datetime.now(timezone.utc)).total_seconds()
            except (TypeError, ValueError, OverflowError):
                advised = 0
        if advised > MAX_BACKOFF:
            raise RuntimeError('NVIDIA Retry-After exceeds the one-minute retry cap. Stop and try later.')
        delay = max(delay, max(0, advised))
    return delay
def api_key():
    for name in ('NVIDIA_API_KEY', 'NVIDIA_KEY'):
        value = os.environ.get(name, '').strip()
        if value:
            return value
    values = {}
    file=ROOT/'.env'
    if file.exists():
        for line in file.read_text(encoding='utf-8-sig').splitlines():
            name,sep,text=line.strip().removeprefix('export ').partition('=')
            if sep and name.strip() in ('NVIDIA_API_KEY', 'NVIDIA_KEY'):
                values[name.strip()] = text.strip().strip('\"\'')
    value = values.get('NVIDIA_API_KEY') or values.get('NVIDIA_KEY')
    if not value:raise RuntimeError('NVIDIA_API_KEY or NVIDIA_KEY is missing. Set it in local .env.')
    return value

def request(content,max_tokens=4096,thinking=True,model=MODEL,timeout=None,*,temperature=0.2,max_attempts=MAX_ATTEMPTS):
    timeout = timeout if timeout is not None else REASONING_TIMEOUT if thinking else TEXT_TIMEOUT
    if timeout <= 0:
        raise ValueError('Request timeout must be positive.')
    if not isinstance(max_attempts, int) or isinstance(max_attempts, bool) or not 1 <= max_attempts <= MAX_ATTEMPTS:
        raise ValueError('Attempts must be an integer between 1 and 7.')
    key=api_key()
    payload={'model':model,'messages':[{'role':'user','content':content}],'max_tokens':max_tokens,'temperature':temperature,'stream':False,'chat_template_kwargs':{'enable_thinking':thinking}}
    if thinking:payload['reasoning_budget']=512
    for attempt in range(max_attempts):
        rate_limit()
        req=urllib.request.Request('https://integrate.api.nvidia.com/v1/chat/completions',data=json.dumps(payload).encode(),headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'})
        try:
            with urllib.request.urlopen(req,timeout=timeout) as response:return json.load(response)
        except urllib.error.HTTPError as error:
            if error.code in [429,502,503,504] and attempt < max_attempts - 1:
                retry_after = error.headers.get('Retry-After') if error.headers else None
                error.close()
                delay = _retry_delay(attempt, retry_after)
                print(f'NVIDIA temporary HTTP {error.code}; retry {attempt + 1}/{max_attempts - 1} in {delay:g}s.', flush=True)
                time.sleep(delay)
                continue
            message=error.read().decode()[:1200].replace(key,'[REDACTED]')
            raise RuntimeError(f'NVIDIA HTTP {error.code}: {message}') from None
        except (urllib.error.URLError, TimeoutError) as error:
            if attempt == max_attempts - 1:
                raise RuntimeError('NVIDIA transport/timeout retries exhausted. Outcome is inconclusive; no candidate accepted.') from None
            delay = _retry_delay(attempt)
            print(f'NVIDIA transport/timeout failure; retry {attempt + 1}/{max_attempts - 1} in {delay:g}s.', flush=True)
            time.sleep(delay)

def parse_json(response):
    choices = response.get('choices') or []
    if not choices or choices[0].get('finish_reason') != 'stop':
        raise ValueError('Model completion did not finish normally; no candidate can be accepted.')
    text = choices[0].get('message', {}).get('content') if choices else None
    if not isinstance(text, str) or not text.strip():
        raise ValueError('Model returned no usable text; no candidate can be accepted.')
    text = text.strip()
    if text.startswith('```'):text=text.split('\n',1)[1].rsplit('```',1)[0]
    return json.loads(text)
