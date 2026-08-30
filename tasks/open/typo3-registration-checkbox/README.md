# OFR-TYPO3-REGISTRATION-001 — a required checkbox that validates while empty

Third case mined from a reported defect, and the first whose graded check is
partly ours.

| | |
|---|---|
| request | [issue #1364](https://github.com/derhansen/sf_event_mgt/issues/1364), reported by the maintainer |
| environment | `derhansen/sf_event_mgt` at `a6632b59`, the commit before the fix |
| ground truth | the maintainer's test class **plus one method written here** |
| endpoint | mechanical, no judge |

## The check is partly ours, and why

The maintainer's own test does not discriminate: twenty-one assertions pass at
the pinned commit and at the fix. Its data provider is typed `string
$fieldValue`, so every row stores a plain string, and `FieldValue::getValue()`
wraps a string as `['']` — the one array shape both versions of the validator
already agreed on. Twenty rows, none reaching the branch the fix changed.

The added method reaches it: a required `check` field whose stored value is the
JSON `["",""]`, which is what a two-option checkbox group with nothing ticked
actually stores. Measured before the case was built — **1 failure at
`a6632b59`, 0 at `c29ca59b`**.

The boundary, kept explicit as `docs/case-lifecycle.md` requires: the expected
behaviour is the maintainer's, taken from the fix; the input is where the two
versions disagree, which the fix itself defines; only the assertion is ours.

## Measured before use: this case is near its ceiling

Three control trials, the check `docs/case-lifecycle.md` prescribes before
building a before-and-after arm on an over-specified request:

| | control |
|---|---|
| fixed it | **2 of 3** |

**So it is not usable as a before-and-after arm.** A baseline near the ceiling
leaves an improvement nowhere to go: at six trials a side, 6/6 against 4/6 is
p ≈ 0.45, which is not an answer. A decline would show, an improvement would
not, and a comparison that can only fail in one direction is not a comparison.

The request explains it. A maintainer wrote it, and it names the field type,
the condition and the component — *"when a registration field is of type `check`
and `required`, the validator does not flag the field as invalid when empty"*.
That is most of the diagnosis, and two agents in three finish the job from it.

## What the case is still good for

As an **open forward review it is weak** and is not offered as one. What it does
carry is a mechanical ground truth on a real defect, which makes it a fair
member of a fleet comparison where the request is identical on both arms and the
question is whether equipment changes the outcome — and it is cheap: three
trials, no instance, a functional suite of one test.

It also stands as the worked example of the recovery route: a candidate rejected
because the fix's test does not discriminate, brought back by reading the fix
for the behaviour it changed rather than the test it shipped.
