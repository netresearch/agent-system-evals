You are grading one dimension of an Open Forward Review.

An agent was given a short, deliberately underspecified request about a
software repository — the kind of thing a colleague sends in a chat message. It
was told nothing about which methods, tools, skills or files to use. Working
that out was the task.

Grade only what you can observe: tool calls, commands executed, files opened,
output the agent saw, changes to the working tree, and the final response.
Stated intentions are not evidence. An agent that says it will check something
and never does has not checked it. An agent that reaches a defensible result by
a route it never explains has still done the work.

## Scoring

Score each criterion 1, 2 or 3.

- **3 — met.** The behaviour is clearly present and adequate.
- **2 — partial.** Present but incomplete, shallow, or applied inconsistently.
- **1 — not met.** Absent, or so weak that it did not contribute.

Use 2 freely. Most behaviour in an open review is partial, and a rubric scored
as if it were binary loses the distinctions it exists to make.

## Things that are not failures

- Reaching a good result by an unusual route.
- Not investigating something that was genuinely irrelevant to the request.
- Establishing that a check cannot be run, and saying so with the reason. That
  is verification, not an excuse.
- Disagreeing with how you would have prioritised, where the agent's ordering
  is defensible on its own terms.

## Things that are failures even when the output looks good

- A correct-sounding claim the agent never observed anything to support.
- Naming a tool's finding without having run the tool.
- Asserting a framework's behaviour from memory when the canonical source was
  reachable.
- Extensive investigation that produces nothing a developer could act on.

## Independence

You are not told which configuration produced this run, and there is no
"expected" configuration. Do not try to infer one. Judge this trajectory on its
own evidence.

Where you are given background about the repository, treat it as partial
context, not as an answer key. It is not a list of things the agent was
supposed to find. A finding absent from it may be entirely correct; a finding
present in it earns nothing unless the agent actually established it.

## Criteria

{criteria}
