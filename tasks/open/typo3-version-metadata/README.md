# OFR-TYPO3-METADATA-001 — the version statements disagree

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

## A second variant of this case exists

`typo3-version-metadata-bare` is the same request against the same commit with
the repository's agent-facing scaffolding removed: the five `AGENTS.md` files,
the Copilot instructions, `CONTRIBUTING.md` and the rendered documentation.

The variable there is not the fleet but the **repository's readiness**. It asks
what the conventions written into a repository are worth to an agent working in
it — and whether the results this benchmark records for a bare control arm are
partly the repository doing the work.
