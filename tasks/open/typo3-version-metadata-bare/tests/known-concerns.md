# Background on the reported defect — verifier-side only

<!-- contamination-markers: nr-xliff-streaming, nr_xliff_streaming -->

**This file must never reach the agent environment.** It ships in `tests/`,
which only the verifier container receives.

**This is not an answer key.** It is partial background so the judge can tell a
conclusion the agent established from one it assumed.

## What disagrees

At the pinned commit:

| Where | Declares |
|---|---|
| `composer.json` | `typo3/cms-core: ^14.3` |
| `ext_emconf.php` | `'typo3' => '13.4.0-13.4.99'` |

Composer would refuse to install the extension on TYPO3 13.4; the extension
manager would refuse it on 14.3. One of the two is wrong and the repository
does not say which.

## What decides it

The code, the tests and the CI matrix, not the metadata. An agent that reads
those and then chooses has done the work; an agent that edits whichever file
makes them match has produced a consistent statement about nothing.

## Known blind spots

- Nothing here judges whether the resulting window is the one the maintainers
  would have chosen. Several are defensible; what is graded is whether the
  choice rests on evidence.
- The extension is at `0.9.0-dev` and marked beta. A finding about its release
  state is outside this case rather than wrong.
