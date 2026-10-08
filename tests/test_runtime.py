import threading
import unittest
from concurrent.futures import CancelledError
from genereticore.contracts import Request
from genereticore.runtime import TaskRuntime

class BlockedBackend:
    def __init__(self):
        self.entered = threading.Event()
        self.release = threading.Event()
        self.calls = []
        self.cancel_count = 0
    def execute(self, request, emit, canceled):
        self.calls.append(request.input_revision)
        self.entered.set()
        self.release.wait(3)
        if canceled(): raise RuntimeError('canceled')
        for i in range(200): emit('partial_text', {'delta': str(i)})
        return {'content': {'text': str(request.input_revision)}}
    def cancel(self):
        self.cancel_count += 1
        self.release.set()
        return True
    def close(self): self.release.set()

def request(rev, stream='live'):
    return Request('text.generate', inputs={'prompt': 'hello'}, input_revision=rev, stream_id=stream)

class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.backend = BlockedBackend()
        self.runtime = TaskRuntime(self.backend, capacity=2, retention=4)
    def tearDown(self): self.runtime.close()
    def active(self):
        job = self.runtime.submit(request(0), 'latest')
        self.assertTrue(self.backend.entered.wait(2))
        return job
    def test_latest_suppresses_active_and_replaces_pending(self):
        old = self.active()
        middle = self.runtime.submit(request(1), 'latest')
        newest = self.runtime.submit(request(2), 'latest')
        self.assertTrue(middle.future.cancelled())
        self.backend.release.set()
        self.assertEqual(newest.future.result(2)['content']['text'], '2')
        self.assertTrue(old.future.cancelled())
        self.assertEqual(self.backend.calls, [0, 2])
        self.assertEqual(self.runtime.snapshot(old.request.request_id)['state'], 'superseded')
        self.assertFalse(any(e['type'] == 'completed' for e in old.events))
    def test_fifo_capacity_and_order(self):
        self.active()
        b = self.runtime.submit(request(1, 'b'))
        c = self.runtime.submit(request(2, 'c'))
        with self.assertRaisesRegex(RuntimeError, 'full'): self.runtime.submit(request(3, 'd'))
        self.backend.release.set()
        b.future.result(2); c.future.result(2)
        self.assertEqual(self.backend.calls, [0, 1, 2])
    def test_cancel_active_and_pending(self):
        active = self.active()
        pending = self.runtime.submit(request(1))
        self.runtime.cancel(pending.request.request_id)
        self.runtime.cancel(active.request.request_id)
        self.assertTrue(pending.future.cancelled())
        self.assertTrue(active.future.cancelled())
        self.assertEqual(self.backend.cancel_count, 1)
    def test_event_retention_is_bounded(self):
        job = self.active(); self.backend.release.set(); job.future.result(2)
        snapshot = self.runtime.snapshot(job.request.request_id)
        self.assertEqual(len(snapshot['events']), 128)
        self.assertTrue(snapshot['events_truncated'])
        self.assertEqual(snapshot['events'][-1]['type'], 'completed')
    def test_older_revision_does_not_supersede_current(self):
        self.active()
        current = self.runtime.submit(request(3), 'latest')
        with self.assertRaises(ValueError): self.runtime.submit(request(2), 'latest')
        self.assertFalse(current.stale)
    def test_close_rejects_new_work(self):
        self.active(); self.runtime.close()
        with self.assertRaises(RuntimeError): self.runtime.submit(request(1))

if __name__ == '__main__': unittest.main()
