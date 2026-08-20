"""Versioned records, and the ninety-odd jobs that predate them.

The migration matters more than the model. Recorded jobs are the only evidence
this project has; a schema that cannot read them is not a schema, it is a reason
to delete history. So the last test here loads every snapshot on the machine and
is skipped where there are none.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "lib"))

import schemas  # noqa: E402


def test_a_record_without_a_version_is_migrated_not_refused():
    """Every snapshot written before 20 August 2026 looks like this."""
    snapshot = schemas.Snapshot.from_dict({"case_id": "X", "fleet": "nr"})
    assert snapshot.schema_version == schemas.SNAPSHOT_VERSION
    assert snapshot.case_id == "X"


def test_the_migration_leaves_the_grade_empty_rather_than_inventing_one():
    """The rubric that scored an old job is not knowable from the file.

    Filling it in would let a comparison believe two jobs were graded alike
    when nothing had checked — which is the defect the grade block was added to
    fix.
    """
    snapshot = schemas.Snapshot.from_dict({"case_id": "X", "fleet": "nr"})
    assert snapshot.grade is None


def test_a_future_version_raises_instead_of_being_read_field_by_field():
    with pytest.raises(schemas.UnreadableRecord) as excinfo:
        schemas.Snapshot.from_dict(
            {"schema_version": 99, "case_id": "X", "fleet": "nr"}
        )
    assert "99" in str(excinfo.value)


def test_a_record_without_a_case_is_refused_with_the_reason():
    with pytest.raises(schemas.UnreadableRecord):
        schemas.Snapshot.from_dict({"fleet": "nr"})


def test_unknown_fields_survive_on_the_raw_record():
    """A reader must not drop what a newer writer added.

    Dropping it silently is how a consumer ends up disagreeing with the file it
    just read.
    """
    snapshot = schemas.Snapshot.from_dict(
        {"case_id": "X", "fleet": "nr", "something_new": 42}
    )
    assert snapshot.raw["something_new"] == 42


def test_a_malformed_file_names_itself(tmp_path):
    path = tmp_path / "nr-snapshot.json"
    path.write_text("{not json")
    with pytest.raises(schemas.UnreadableRecord) as excinfo:
        schemas.Snapshot.load(path)
    assert "nr-snapshot.json" in str(excinfo.value)


def test_the_version_is_the_first_key_a_reader_meets():
    stamped = schemas.stamp({"case_id": "X"}, schemas.SNAPSHOT_VERSION)
    assert next(iter(stamped)) == "schema_version"


def test_every_recorded_snapshot_on_this_machine_still_loads():
    """The one that would actually hurt.

    Skipped where `jobs/` is absent — on CI it always is, because recorded
    artifacts are not committed.
    """
    snapshots = sorted((ROOT / "jobs").glob("*/nr-snapshot.json"))
    if not snapshots:
        pytest.skip("no recorded jobs on this machine")

    failures = []
    for path in snapshots:
        try:
            schemas.Snapshot.load(path)
        except schemas.UnreadableRecord as exc:
            # A snapshot with no case_id is a broken record rather than a
            # migration failure; report it as itself.
            failures.append(f"{path.parent.name}: {exc}")
    assert failures == [], f"{len(failures)} recorded snapshot(s) no longer load"


def test_experiment_and_calibration_versions_exist():
    assert schemas.EXPERIMENT_VERSION >= 1
    assert schemas.CALIBRATION_VERSION >= 1


# --------------------------------------------------------------------------
# benchmark version
# --------------------------------------------------------------------------


def load_script(name: str):
    import importlib.machinery
    import importlib.util

    spec = importlib.util.spec_from_loader(
        name,
        importlib.machinery.SourceFileLoader(name, str(ROOT / "scripts" / name)),
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


version_script = load_script("benchmark-version")


def test_the_version_file_parses_as_three_parts():
    parts = (ROOT / "VERSION").read_text().strip().split(".")
    assert len(parts) == 3 and all(p.isdigit() for p in parts)


def test_a_rubric_change_asks_for_a_minor_bump():
    """The rule that gets skipped.

    A rubric edit is cheap to make and changes what every future number means.
    The first version of this predicate compared a glob literally with
    `str.startswith`, so `tasks/*/*/tests/` matched nothing and the check
    reported "nothing changed that moves a score" for exactly this input.
    """
    hits = version_script.demanded(
        ["tasks/open/typo3-extension-review/tests/evidence/judge.toml"]
    )
    assert [part for _, part, _ in hits] == ["minor"]


def test_a_case_definition_change_asks_for_a_major_bump():
    hits = version_script.demanded(["tasks/open/typo3-extension-review/task.toml"])
    assert [part for _, part, _ in hits] == ["major"]


def test_the_dimension_registry_is_a_major_bump():
    hits = version_script.demanded(["dimensions.toml"])
    assert [part for _, part, _ in hits] == ["major"]


def test_documentation_moves_no_score():
    assert version_script.demanded(["docs/governance.md", "README.md"]) == []


def test_expectations_are_a_patch_because_no_judge_reads_them():
    hits = version_script.demanded(["expectations/OFR-TYPO3-EXT-001.md.enc"])
    assert [part for _, part, _ in hits] == ["patch"]
