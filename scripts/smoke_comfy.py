"""Explicit local end-to-end test against an already-running isolated Comfy instance."""
import argparse
import json
import time
from urllib.request import Request, urlopen

parser = argparse.ArgumentParser()
parser.add_argument('--url', default='http://127.0.0.1:8003')
args = parser.parse_args()
if not args.url.startswith(('http://127.0.0.1:', 'http://localhost:')):
    parser.error('This smoke test is loopback-only')

def call(path, body=None):
    req = Request(args.url + path, data=json.dumps(body).encode() if body is not None else None,
                  headers={'Content-Type':'application/json'})
    with urlopen(req, timeout=30) as response: return json.load(response)

def finish(id):
    deadline = time.monotonic() + 120
    while time.monotonic() < deadline:
        snapshot = call('/genereticore/tasks/' + id)
        if snapshot['state'] in {'completed','failed','canceled','superseded'}: return snapshot
        time.sleep(.1)
    raise RuntimeError('Task timed out')

info = call('/object_info')
assert all(n in info for n in ('GeneretiCoreText','GeneretiCoreVision','GeneretiCoreDecision','GeneretiCoreValidateDecision','GeneretiCoreResult','GeneretiCoreChoiceValue','GeneretiCoreTutorial'))
assert 'GeneretiSDXSGenerate' not in info, 'The isolated test must not register legacy duplicates'
body = {'task':'text.generate','model':'qwen3-0.6b','inputs':{'prompt':'Describe a calm scene. /no_think'},
        'options':{'max_tokens':64},'policy':'latest','stream_id':'smoke','input_revision':0}
first = call('/genereticore/tasks', body)['request_id']
body['input_revision'] = 1
second = call('/genereticore/tasks', body)['request_id']
result = finish(second)
assert result['state'] == 'completed', result
assert finish(first)['state'] == 'superseded'
assert result['events'][-1]['payload']['content']['text'].strip()
body.update({'stream_id':'cancel-smoke','input_revision':0,'options':{'max_tokens':2048}})
canceled = call('/genereticore/tasks', body)['request_id']
# Wait for started so this verifies native cancellation rather than removing pending work.
for _ in range(100):
    snapshot = call('/genereticore/tasks/' + canceled)
    if any(e['type'] == 'started' for e in snapshot['events']): break
    time.sleep(.05)
assert call('/genereticore/tasks/' + canceled + '/cancel', {})['canceled']
assert finish(canceled)['state'] == 'canceled'
body.update({'stream_id':'restart-smoke','options':{'max_tokens':32}})
restarted = call('/genereticore/tasks', body)['request_id']
assert finish(restarted)['state'] == 'completed'
queued = call('/prompt', {'client_id':'genereticore-smoke', 'prompt': {'1': {
    'class_type':'GeneretiCoreDecision', 'inputs': {'model':'qwen3-0.6b','prompt':'Choose a palette for a calm scene.',
    'choices_json':'["blue", "orange"]','max_tokens':128}}}})['prompt_id']
for _ in range(300):
    history = call('/history/' + queued)
    if queued in history:
        assert history[queued]['status']['status_str'] == 'success', history
        assert history[queued]['outputs']['1']['text']
        break
    time.sleep(.1)
else: raise RuntimeError('Comfy queue did not complete')
print(json.dumps({'registered_nodes':7,'latest_wins':'passed','active_cancel':'passed','helper_restart':'passed',
    'queued_decision':'passed','local_text_timings':result['events'][-1]['payload'].get('timings')}, indent=2))
