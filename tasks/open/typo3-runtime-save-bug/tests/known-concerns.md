# Background on the reported defect — verifier-side only

<!-- contamination-markers: nr-textdb, nr_textdb, SYSTEM_MAIL_FOOTER_HTML_MFAG, tx_nrtextdb_domain_model_translation -->

**This file must never reach the agent environment.** It ships in `tests/`,
which only the verifier container receives. Checked by
`scripts/contamination-check`.

**This is not an answer key.** It is partial background so the judge can tell a
mechanism the agent established from one it guessed. A correct diagnosis absent
from this list is still correct.

## What was reported

A production report against nr-textdb 2.0.11 on TYPO3 12.4: saving a
translation through the backend module does not update the record. Each save
silently inserts an additional row with `sys_language_uid = 0` and unresolved
foreign keys — `environment = 0, component = 0, type = 0` — for the same
placeholder. Once that row exists, every further save aborts with a 503,
because the insert collides with the unique key
`translation (sys_language_uid, pid, environment, component, type, placeholder, deleted)`.

The sharpest detail: **the first failed save shows no error at all.** The
dialog closes, the loader runs, and the record still holds the old value. The
editor is told nothing.

## What the environment contains

The instance is TYPO3 13.4 with the extension active at the pinned commit — the
commit immediately before the fix. The database holds the state the report
describes: the valid record, and beside it the orphaned row.

That state is **seeded data, not an injected defect**. The defect is the
extension's own and is in its code. The rows are seeded because reproducing
them needs a click in the backend module and this environment has no web
server; a developer handed this ticket receives exactly this situation.

| uid | pid | lang | env | comp | type | placeholder |
|---|---|---|---|---|---|---|
| 1 | 1 | 0 | 1 | 1 | 1 | SYSTEM_MAIL_FOOTER_HTML_MFAG |
| 2 | 1 | 0 | 0 | 0 | 0 | SYSTEM_MAIL_FOOTER_HTML_MFAG |

## What a good diagnosis reaches

Recorded so the judge can recognise established work, not as a checklist. The
first point is the root cause as the merged fix confirms it; the rest follow
from it.

- **Every persisted property of the four domain models is declared `private`.**
  Extbase hydrates and dirty-checks entities from `AbstractDomainObject`, the
  parent class, which cannot reach a property private to the subclass. So the
  references the record should carry — environment, component, type — never
  arrive, and the save writes zeros in their place. That is where the orphaned
  row comes from, and it is why the row carries `0/0/0` rather than arbitrary
  values.
- The consequence is wider than the report: a visibility problem in hydration
  breaks every request that maps one of these records, not only the save.
  Noticing that the report understates the damage is a strength, not a
  digression.
- Two distinct failure modes follow, and they need separate explanations: the
  silent one on the first attempt, and the unique-key collision on every later
  one.
- The orphaned row is damage that persists independently of any code fix. A
  complete answer separates repairing the code from clearing the data.

The merged fix (PR #101) changes those properties to `protected`, routes the
controller through a raw lookup instead of the language-restricted one, gives
an already-present language record its own update path, and wraps `persistAll`
in a `try`/`catch` that raises a flash message — the part that ends the
silence. An answer is not measured against that diff: several corrections are
defensible, and an agent that reaches the visibility cause and proposes a
different remedy has done the work this case asks for.

## Known blind spots

- Nothing here evaluates whether the agent's proposed fix is the one the real
  change made. Several corrections are defensible.
- The instance has no web server, so nothing here judges frontend or backend
  HTTP behaviour.
- The report came from TYPO3 12.4; the instance runs 13.4, the line the pinned
  commit supports. Where that difference matters to a finding, the agent
  saying so is worth more than the finding.
