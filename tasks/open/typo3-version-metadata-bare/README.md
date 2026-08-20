# OFR-TYPO3-METADATA-001-BARE — the same task, in an unprepared repository

```
Our extensions have to state which TYPO3 versions they support, and this one's
statements do not agree with each other. Sort it out.
```

Everyday maintenance, and a defect that was found in production rather than
invented for this case. At the pinned commit, `netresearch/nr-xliff-streaming`
declares:

| Where | What it says |
|---|---|
| `composer.json` | `typo3/cms-core: ^14.3` |
| `ext_emconf.php` | `'typo3' => '13.4.0-13.4.99'` |

Those cannot both be true. Composer says the extension needs TYPO3 14.3 or
newer; the extension manager says it runs on 13.4 and nothing else. An install
from the Extension Repository and an install through Composer would disagree
about whether the extension may be installed at all.

## Why it is an open case and not a contract eval

The prompt does not say which file is wrong, and neither does the repository.
Deciding that is the work: the code has to be read to see which line it
actually supports, and the answer has to say so rather than making the two
statements match by editing whichever one is easier.

An agent that simply copies one constraint into the other satisfies the letter
of the request and leaves the extension declaring something nobody checked.
The rubric grades that apart from a fix that establishes the supported line
first.

## What is graded mechanically

- The two declarations agree after the change.
- The declaration matches the line the code supports, established rather than
  assumed.
- The change is confined to the metadata — this is not a licence to alter the
  extension's behaviour.

## What is different here, and why the target is modified

This is `typo3-version-metadata` against the same commit with the repository's
agent-facing scaffolding removed at build time: the five `AGENTS.md` files, the
Copilot instructions, `CONTRIBUTING.md` and the rendered `Documentation/`. The
code, the tests, the CI workflows and both version declarations are untouched.

The methodology otherwise forbids modifying a target
([open-forward-review.md](../../../docs/open-forward-review.md) section 3). It
is allowed here because the modification **is** the measurement, and it is
declared in the case identifier, in `metadata.variant`, in the Dockerfile and
here rather than in a footnote.

## The question

Every result this benchmark has recorded treats the repository as a constant
and the fleet as the variable. But the targets are Netresearch repositories
that have already been through these skills: `AGENTS.md` files, documented
conventions, a harness. A control arm working in one of them inherits that for
free, and any comparison of fleets inside it measures what the skills add *on
top of a repository they already shaped*.

This pair turns the variable around. Same request, same fleet, same commit —
one repository that says how it works and one that does not. If the prepared
repository carries most of the benefit, then the way to give an agent a good
day is to write the conventions down once, not to hand it more skills.

