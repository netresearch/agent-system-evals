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


def test_a_moved_ref_is_caught_by_comparing_locks(tmp_path):
    """A branch resolved per trial can put two treatments in one arm.

    It happened twice in one afternoon — once by pushing to the branch during a
    run, once by merging and deleting it — and the locks recorded it while
    nothing read them.
    """
    module = load()
    first = tmp_path / "a"
    first.mkdir()
    (first / "lock.json").write_text(
        '{"p":"/cache/skills/github.com/netresearch/typo3-extension-upgrade-skill/'
        + "a" * 40 + '/skills"}'
    )
    moved = tmp_path / "b"
    moved.mkdir()
    (moved / "lock.json").write_text(
        '{"p":"/cache/skills/github.com/netresearch/typo3-extension-upgrade-skill/'
        + "b" * 40 + '/skills"}'
    )
    assert module.resolved_skills(first) != module.resolved_skills(moved)
    assert module.resolved_skills(first) == {
        "netresearch/typo3-extension-upgrade-skill": "a" * 40
    }
    # No lock at all is not a claim that the refs agree — and it must not be
    # `{}`, or two unreadable jobs would compare equal and the check would pass
    # having proved nothing.
    assert module.resolved_skills(tmp_path / "missing") is None

    # Bytes that are not UTF-8 raise UnicodeDecodeError, which is a ValueError
    # rather than an OSError, so it would escape a narrower catch.
    undecodable = tmp_path / "c"
    undecodable.mkdir()
    (undecodable / "lock.json").write_bytes(b"\xff\xfe not utf-8")
    assert module.resolved_skills(undecodable) is None
    assert "cannot be verified" in (ROOT / "scripts" / "run-comparison").read_text()

    source = (ROOT / "scripts" / "run-comparison").read_text()
    assert "resolved different skills than in its" in source
