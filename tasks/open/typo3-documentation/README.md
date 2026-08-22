# OFR-TYPO3-DOCS-001 — give it documentation

```
This extension has no documentation on docs.typo3.org. Please give it some.
```

Everyday work, and the third of the low-level cases. `netresearch/nr-image-sitemap`
is a small data provider for the SEO extension's sitemap generation. It has a
README, an architecture note and a `Classes/` directory. It has no
`Documentation/` at all, which is its actual state and not something arranged
for this case.

## Ground truth, decided by the framework

docs.typo3.org renders from a particular shape: a `guides.xml` naming the
project, an `Index.rst`, and a toctree whose every entry resolves to a document
that exists. A collector checks all three after the agent finishes and prints
one verdict line.

The toctree check is the one worth having. An index listing pages nobody wrote
looks complete in a diff and fails at render, and that is exactly what a shallow
run produces.

The check was written against four recorded states before it was trusted:
nothing at all, a skeleton whose index points into the void, a complete tree,
and the complete tree with one page removed again. It named the missing document
each time.

Writing it produced two of its own failures first, both found by that
counter-probe rather than by reading: `guides.xml` declares a default XML
namespace, so a plain `.//project` lookup matched nothing and reported a valid
file as broken; and a single regex for the toctree matched no ordinary index at
all, because every real one has a blank line between the options and the
entries. A check that silently finds zero entries reports a skeleton as
complete.

## What the judge is asked

Whether the text describes *this* extension or a template with its name
substituted in — the structural check cannot see the difference, and a template
passes it perfectly. Whether the current layout was established or reproduced
from memory: `Settings.cfg` was replaced by `guides.xml`, and the canonical
documentation was reachable during the run. Whether anything was asserted that
the repository does not support. And whether the diff is documentation and
nothing else.

## Status

**Never run.** The case validates, its ground-truth check is verified against
four recorded states, and the sandbox audit is clean; no trial has been recorded
against it.

## Reviewed by

Nobody yet. `docs/governance.md` requires a case to be admitted by someone who
did not write it; this repository has been written by one person, so the field
is empty rather than filled in by its author.

## What capability this task plausibly needs

Recorded so that a skill-invocation count of zero can be read. A zero means one of two
things — the capability was on offer and was not selected, or it was not on offer — and
those are findings about different things (see issue #24).

Writing TYPO3 extension documentation from nothing. `netresearch/typo3-docs-skill` is in `nr`
and names creating extension documentation.

**Present, and selected** — invoked in three trials of three on Haiku. What failed there was
the second hop: the correct `guides.xml` skeleton sits behind a reference file no trial read.
