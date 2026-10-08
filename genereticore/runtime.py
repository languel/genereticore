from __future__ import annotations
from collections import OrderedDict, deque
from concurrent.futures import Future
from dataclasses import dataclass, field
import threading
import time

from .contracts import Request

TERMINAL = {"completed", "canceled", "failed", "superseded"}

@dataclass
class Job:
    request: Request
    future: Future = field(default_factory=Future)
    events: deque = field(default_factory=lambda: deque(maxlen=128))
    state: str = "queued"
    sequence: int = 0
    stale: bool = False
    cancel_event: threading.Event = field(default_factory=threading.Event)

    @property
    def canceled(self):
        return self.cancel_event.is_set()
    submitted_at: float = field(default_factory=time.time)
    finished_at: float | None = None

class TaskRuntime:
    """One active model task; bounded pending jobs and bounded event/result retention."""
    def __init__(self, backend, capacity=4, retention=64):
        if capacity < 1 or retention < capacity + 1:
            raise ValueError("Invalid queue bounds")
        self.backend = backend
        self.capacity, self.retention = capacity, retention
        self.jobs = OrderedDict()
        self.pending = deque()
        self.active = None
        self._closed = False
        self._condition = threading.Condition(threading.RLock())
        self._worker = threading.Thread(target=self._work, name="GeneretiCore", daemon=True)
        self._worker.start()

    def _emit(self, job, kind, payload=None):
        with self._condition:
            if job.stale or job.canceled:
                if kind not in {"superseded", "canceled"}:
                    return
            job.sequence += 1
            job.events.append({"sequence": job.sequence, "type": kind,
                "request_id": job.request.request_id, "input_revision": job.request.input_revision,
                "timestamp": time.time(), "payload": payload or {}})
            if kind in TERMINAL:
                job.state = kind
                job.finished_at = time.time()
            self._condition.notify_all()

    def _evict(self):
        for id, job in list(self.jobs.items()):
            if len(self.jobs) < self.retention:
                break
            if job.future.done() and job is not self.active:
                del self.jobs[id]

    def submit(self, request: Request, policy="fifo"):
        if policy not in {"fifo", "latest"}:
            raise ValueError("policy must be fifo or latest")
        with self._condition:
            if self._closed:
                raise RuntimeError("Runtime closed")
            if request.request_id in self.jobs:
                raise ValueError("Duplicate request_id")
            if policy == "latest":
                if any(j.request.stream_id == request.stream_id and j.request.input_revision > request.input_revision for j in self.jobs.values()):
                    raise ValueError("Input revision predates the current stream revision")
                matching = [j for j in self.pending if j.request.stream_id == request.stream_id]
                if self.active and self.active.request.stream_id == request.stream_id:
                    matching.append(self.active)
                if any(j.request.input_revision > request.input_revision for j in matching):
                    raise ValueError("Input revision predates the current stream revision")
                # Check capacity BEFORE invalidating the active result.
                if len(self.pending) - sum(j in self.pending for j in matching) >= self.capacity:
                    raise RuntimeError("Inference queue is full")
                for old in matching:
                    old.stale = True
                    if old in self.pending:
                        self.pending.remove(old)
                        self._emit(old, "superseded", {"backend_canceled": False})
                        old.future.cancel()
            elif len(self.pending) >= self.capacity:
                raise RuntimeError("Inference queue is full")
            self._evict()
            if len(self.jobs) >= self.retention:
                raise RuntimeError("Job retention is full")
            job = Job(request)
            self.jobs[request.request_id] = job
            self.pending.append(job)
            self._emit(job, "queued", {"queue_depth": len(self.pending)})
            self._condition.notify_all()
            return job

    def cancel(self, request_id):
        with self._condition:
            job = self.jobs[request_id]
            if job.state in TERMINAL:
                return False
            job.cancel_event.set()
            if job in self.pending:
                self.pending.remove(job)
                self._emit(job, "canceled", {"backend_canceled": False, "pending_removed": True})
                job.future.cancel()
                return True
            if self.active is job:
                # The worker cannot start another job while this lock is held.
                stopped = self.backend.cancel()
                self._emit(job, "canceled", {"backend_canceled": stopped})
                job.future.cancel()
                return True
            return False

    def snapshot(self, request_id, after=0):
        with self._condition:
            job = self.jobs[request_id]
            return {"request_id": request_id, "input_revision": job.request.input_revision,
                "state": job.state, "stale": job.stale, "queue_depth": len(self.pending),
                "events": [e for e in job.events if e["sequence"] > after],
                "cursor": job.sequence,
                "events_truncated": bool(job.events and after < job.events[0]["sequence"] - 1),
                "result_age_ms": (time.time() - job.finished_at) * 1000 if job.finished_at else None}

    def status(self):
        with self._condition:
            return {"busy": self.active is not None, "queue_depth": len(self.pending),
                "capacity": self.capacity, "active_request_id": self.active.request.request_id if self.active else None}

    def _work(self):
        while True:
            with self._condition:
                self._condition.wait_for(lambda: self.pending or self._closed)
                if self._closed:
                    return
                job = self.pending.popleft()
                self.active = job
                job.state = "running"
                self._emit(job, "loading", {"queue_wait_ms": (time.time() - job.submitted_at) * 1000})
            try:
                result = self.backend.execute(job.request, lambda kind, data: self._emit(job, kind, data), job.cancel_event.is_set)
                with self._condition:
                    if job.canceled:
                        pass
                    elif job.stale:
                        self._emit(job, "superseded", {"backend_canceled": False, "result_suppressed": True})
                        job.future.cancel()
                    else:
                        self._emit(job, "completed", result)
                        job.future.set_result(result)
            except Exception as exc:
                with self._condition:
                    if job.canceled:
                        pass
                    elif job.stale:
                        self._emit(job, "superseded", {"backend_canceled": False})
                        job.future.cancel()
                    else:
                        self._emit(job, "failed", {"message": str(exc)})
                        job.future.set_exception(exc)
            finally:
                with self._condition:
                    self.active = None
                    self._condition.notify_all()

    def close(self):
        with self._condition:
            if self._closed:
                return
            self._closed = True
            for job in list(self.pending) + ([self.active] if self.active else []):
                self.cancel(job.request.request_id)
            self._condition.notify_all()
        self._worker.join(timeout=10)
        self.backend.close()
