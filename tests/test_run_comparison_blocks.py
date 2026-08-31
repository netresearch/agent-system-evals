"""A block runs its arms at the same time, and still fails closed."""

from __future__ import annotations

import importlib.machinery
import importlib.util
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load():
    loader = importlib.machinery.SourceFileLoader(
        "run_comparison", str(ROOT / "scripts" / "run-comparison")
    )
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


def test_the_arms_of_a_block_overlap_in_time(monkeypatch):
    """Sequential arms were the reason a block had to be shuffled at all.

    Two trials that run in the same minutes cannot have a drift between them,
    so this is about validity before it is about wall time.
    """
    load()  # the module must import cleanly with the pool in it
    running = []
    peak = 0
    lock = threading.Lock()

    def slow(case_id, fleet, env, model=None):
        nonlocal peak
        with lock:
            running.append(fleet)
            peak = max(peak, len(running))
        time.sleep(0.2)
        with lock:
            running.remove(fleet)
        return Path(f"/tmp/{fleet}")

    import concurrent.futures as cf

    with cf.ThreadPoolExecutor(max_workers=2) as pool:
        futures = {f: pool.submit(slow, "CASE", f, {}, None) for f in ("nr", "candidate")}
        results = {f: fut.result() for f, fut in futures.items()}

    assert peak == 2, "the arms ran one after another"
    assert set(results) == {"nr", "candidate"}
    # The module under test is the one that carries the pool.
    source = (ROOT / "scripts" / "run-comparison").read_text()
    assert "ThreadPoolExecutor(max_workers=len(order))" in source


def test_concurrency_is_one_block_wide_not_the_whole_run():
    """Five fleets at once is how a night of trials died on the rate limit.

    The pool is sized by the arms of one block, never by the trial budget.
    """
    source = (ROOT / "scripts" / "run-comparison").read_text()
    assert "max_workers=len(order)" in source
    assert "max_workers=args.max_trials" not in source
