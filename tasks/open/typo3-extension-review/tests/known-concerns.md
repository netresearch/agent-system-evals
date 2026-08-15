# Background on the reviewed repository — verifier-side only

<!-- contamination-markers: DumpFileTrait, TableDifferenceTrait, SyncImportTask, TableStateSyncModuleController, nr-sync, t3x-sync -->


**This file must never reach the agent environment.** It is copied into the
verifier container with `tests/`, which the agent cannot read. Checked by
`scripts/contamination-check`.

**This is not an answer key.** It is partial background, recorded so that the
judge can tell a substantiated finding from a plausible guess. A correct
finding absent from this list is still correct. A finding that appears here
earns nothing unless the agent actually established it from the code.

## How this background was obtained

The target is pinned at the parent of a later change in the same repository
that addressed several of the items below. That change is not reachable from
the agent environment: the working copy is a single-commit fetch with the
remote removed, and the network allowlist excludes the target's forge.

## State of the target at the reviewed commit

**Framework version.** The extension declares `typo3/cms-core ^12.4` and
supports no later line. TYPO3 v14.3 is the current LTS. Version currency is
therefore a legitimate and significant finding. Note that "supports v14" cannot
be established from a constraint alone — a constraint states what is permitted,
not what was tested.

**Suppressed static-analysis findings.** Three security findings carry inline
suppression comments referencing triage issues, and are suppressed rather than
resolved:

1. A scheduler task builds a temporary file path by concatenating a fixed
   directory with an iteration key, then deletes it. Suppressed as
   non-user-input.
2. A trait builds a SQL `WHERE` clause by string concatenation and passes it to
   a query builder, with quoting applied by hand rather than parameter binding.
   Suppressed as adequately escaped.
3. State is written to disk with `serialize()` and read back with
   `unserialize()`, which is an object-injection surface regardless of the
   current contents.

The interesting property for grading is that a scan run at this commit reports
*clean*, because all three are suppressed. Treating a clean scan as an absence
of problems is exactly the failure mode this case can observe. An agent that
reads the suppressions and questions them is doing better work than one that
reports a green run.

**Toolchain.** PHPStan, Rector, PHP-CS-Fixer, phplint and PHPUnit are all
installed and runnable, and the Makefile exposes them. There is no excuse for
an unverified claim about what any of them would report.

**Documentation and packaging.** The extension ships `Documentation/`,
`README.md`, `SECURITY.md`, `CHANGELOG.md` and `ext_emconf.php`. No `AGENTS.md`
exists at this commit, so context has to be established from ordinary project
files.

**Dependencies.** No `composer.lock` is committed, which is normal for a
library and is not a defect. The environment's installed set was pinned by the
case, not by the target; see `environment/target-composer.lock`.

## Known blind spots in this background

- No judgement is recorded here about test coverage adequacy.
- Nothing here evaluates the extension's runtime behaviour; this case is
  repository-level only (ADR 0006).
- The three items above are the ones a later change addressed. They are
  certainly not the only defensible findings, and the list must not be read as
  exhaustive.
