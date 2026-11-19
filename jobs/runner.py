"""A minimal single-worker background job queue.

Namecheap Stellar Plus shared hosting has no Celery/Redis and a hard cap on
concurrent processes, so this deliberately avoids spawning new processes: one
background thread pulls jobs off an in-memory queue and runs them one at a
time. The web request only ever enqueues a job and polls its status — see
templates that poll `/.../job/<id>/status`.

This only works correctly with a single Passenger application process (see
the deployment notes) — multiple worker processes would each have their own
queue and never see each other's jobs.
"""

import logging
import queue
import threading
import time
import uuid

logger = logging.getLogger(__name__)

_jobs = {}
_lock = threading.Lock()
_queue: "queue.Queue" = queue.Queue()
_worker_started = False


def _worker_loop():
    while True:
        job_id, target, args, kwargs = _queue.get()
        job = _jobs[job_id]
        job["status"] = "running"
        job["started_at"] = time.time()
        try:
            result = target(job, *args, **kwargs)
            job["result"] = result
            job["status"] = "done"
        except Exception as e:
            logger.exception("Job %s failed", job_id)
            job["status"] = "error"
            job["error"] = str(e)
        finally:
            job["finished_at"] = time.time()


def _ensure_worker():
    global _worker_started
    with _lock:
        if not _worker_started:
            t = threading.Thread(target=_worker_loop, daemon=True)
            t.start()
            _worker_started = True


def submit_job(target, *args, **kwargs) -> str:
    """Queue `target(job, *args, **kwargs)` to run in the background. `target`
    should periodically call update_progress(job, ...) and return a JSON-
    serializable result dict."""
    _ensure_worker()
    job_id = uuid.uuid4().hex[:12]
    job = {
        "id": job_id,
        "status": "queued",
        "progress": {"done": 0, "total": 0, "current": "", "phase": "queued"},
        "result": None,
        "error": None,
        "created_at": time.time(),
    }
    with _lock:
        _jobs[job_id] = job
    _queue.put((job_id, target, args, kwargs))
    return job_id


def get_job(job_id):
    return _jobs.get(job_id)


def update_progress(job, done, total, current="", phase=""):
    job["progress"] = {"done": done, "total": total, "current": current, "phase": phase}
