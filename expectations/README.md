# Case expectations

What an experienced reviewer knows about each target: the findings a case
expects, the mechanisms behind them, and the identifiers that give them away.
One encrypted file per case, `<case-id>.md.enc`. The decrypted working copies
sit beside them and are ignored by git.

```
scripts/expectations decrypt      # read them
scripts/expectations encrypt      # after editing
scripts/expectations check        # every case has one, all decrypt
```

The key comes from `EVALS_EXPECTATIONS_KEY` or
`~/.config/agent-system-evals/expectations.key`. Generate one with
`scripts/expectations keygen`; it is printed once and cannot be recovered from
the ciphertext.

## Why they moved here

They used to live in `tasks/*/tests/known-concerns.md`, and ADR 0005 and the
dataset manifest both said the expectations of a public case were not public.
They were — committed, in a public repository, from the day each case was
written. What those files had was *verifier isolation*: the agent's container
never held them. That is a different property, and describing it as secrecy
meant nobody looked.

Moving them costs nothing in grading. They were listed in each judge's `files`,
and RewardKit's agent path ignores `files` entirely
([docs/instrument-failures.md](../docs/instrument-failures.md), failure 6), so
no judge has ever read one. They were public and unused.

## What this does not fix

Git history still holds every plaintext version, and the repository is public.
The five cases that existed before 20 August 2026 are burned: their
expectations have been readable for as long as they have existed, and no
history rewrite can un-publish what was already fetchable. Their scores remain
useful for development and are not evidence about any system that could have
read them.

This mechanism protects the cases written from here on.
