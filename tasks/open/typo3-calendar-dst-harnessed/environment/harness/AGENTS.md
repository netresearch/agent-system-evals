<!-- FOR AI AGENTS - Human readability is a side effect, not a goal -->
<!-- Managed by agent: keep sections and order; edit content, not structure -->
<!-- Last updated: 2026-08-29 | Last verified: 2026-08-29 -->

# AGENTS.md

**Precedence:** the **closest `AGENTS.md`** to the files you're changing wins. Root holds global defaults only.

## Commands (verified against .github/workflows and the installed tree)
> This extension keeps its dev dependencies in a SECOND composer tree under `.Build/`.
> Binaries are not in `vendor/bin`. Install with `composer install` in both `.` and `.Build`.

<!-- AGENTS-GENERATED:START commands -->
| Task | Command | ~Time |
|------|---------|-------|
| Lint | .Build/vendor/bin/php-cs-fixer fix --dry-run --config .Build/php-cs-fixer/.php-cs-fixer.php | ~10s |
| Format | .Build/vendor/bin/php-cs-fixer fix --config .Build/php-cs-fixer/.php-cs-fixer.php | ~5s |
| Test (unit) | .Build/vendor/bin/phpunit -c .Build/phpunit/UnitTests.xml | ~30s |
| Test (functional) | typo3DatabaseDriver=pdo_sqlite .Build/vendor/bin/phpunit -c .Build/phpunit/FunctionalTests.xml | ~60s |
<!-- AGENTS-GENERATED:END commands -->

> If commands fail, verify against Makefile/package.json/composer.json or ask user to update.

## Response Style
- Answer first, elaborate only if needed. No sycophantic openers ("Great question!", "Absolutely!").
- For yes/no or status questions, lead with the answer.
- Skip preamble. Match response length to task complexity.

## Workflow
1. **Before coding**: Read nearest `AGENTS.md` + check Golden Samples for the area you're touching
2. **After each change**: Run the smallest relevant check (lint → typecheck → single test)
3. **Before committing**: Run full test suite if changes affect >2 files or touch shared code
4. **Before claiming done**: Run verification and **show output as evidence** — never say "try again", "should work now", "tested", "verified", or "all green" without pasted command output in the same turn

## File Map
<!-- AGENTS-GENERATED:START filemap -->
```
Classes/         → PHP classes (PSR-4)
Tests/           → test suites
Documentation/   → documentation (RST/MD)
Resources/       → templates and assets
Configuration/   → framework configuration
Makefile/        → project files
```
<!-- AGENTS-GENERATED:END filemap -->

## Golden Samples (follow these patterns)
<!-- AGENTS-GENERATED:START golden-samples -->
| For | Reference | Key patterns |
|-----|-----------|--------------|
| Controller | `Classes/Controller/UserRegistrationController.php` |  (class) |
| Reference | `ext_localconf.php` |  (class) |
| Service | `Classes/Service/EventCacheService.php` |  (class) |
| Test | `Tests/Functional/ViewHelpers/TitleViewHelperTest.php` | test structure |
<!-- AGENTS-GENERATED:END golden-samples -->

## Heuristics (quick decisions)
<!-- AGENTS-GENERATED:START heuristics -->
| When | Do |
|------|-----|
| Adding class | Follow PSR-4 in `Classes/` or `src/` |
| Adding controller | Create in `Classes/Controller/` |
| Adding service | Create in `Classes/Service/` |
| Running tasks | Check `make help` for available commands |
| Committing | Use [TAG] prefix style |
| Merging PRs | Squash and merge |
| Adding dependency | Ask first - we minimize deps |
| Unsure about pattern | Check Golden Samples above |
<!-- AGENTS-GENERATED:END heuristics -->

## Repository Settings
<!-- AGENTS-GENERATED:START repo-settings -->
- **Default branch:** `main`
<!-- AGENTS-GENERATED:END repo-settings -->

<!-- AGENTS-GENERATED:START ci-rules -->
## CI/Quality Gates
> Platform: github-actions

### Version Matrix
- PHP 8.1, 8.2, 8.3

### Quality Gates (must pass before merge)
- `phpstan`
- `php-cs-fixer`
- `phpunit`
<!-- AGENTS-GENERATED:END ci-rules -->

## Boundaries

### Always Do
- Run pre-commit checks before committing
- Add tests for new code paths
- Use conventional commit format: `type(scope): subject`
- Use **atomic commits** (one logical change per commit); preserve signatures, keep bisection useful
- **Show test output as evidence before claiming work is complete** — never say "try again", "should work now", "tested", "verified", or "all green" without pasted command output
- Before any edit, verify `pwd` resolves inside the intended repo worktree — not `.bare/`, not `~/.claude/skills/…`, not `~/.claude/plugins/cache/…` (those are read-only caches that get clobbered on update)
- For upstream dependency fixes: run **full** test suite, not just affected tests
- Force-push only with `--force-with-lease`
- Follow PSR-12 coding standards and PHP unknown features

### Ask First
- Adding new dependencies
- Modifying CI/CD configuration
- Changing public API signatures
- Running full e2e test suites
- Repo-wide refactoring or rewrites
- Operations that touch >3 repos (produce a dry-run plan first)

### Never Do
- Commit secrets, credentials, or sensitive data
- Modify vendor/, node_modules/, or generated files
- Push directly to main/master branch — open a PR
- Merge a PR before all review threads are resolved
- Squash commits during merge or rebase unless the user explicitly asked
- Edit installed skill/plugin cache paths (`~/.claude/skills/`, `~/.claude/plugins/cache/`, `**/.bare/**`) — always the source worktree
- Reply to review comments with bare "Addressed" or "Fixed" — cite the resolving commit SHA
- Delete migration files or schema changes
- Use `secrets: inherit` in reusable GitHub Actions workflows (pass secrets explicitly)
- Commit composer.lock without composer.json changes
- Modify core framework files

## Contributing (for AI agents)
- **Comprehension**: Understand the problem before submitting code. Read the linked issue, understand *why* the change is needed, not just *what* to change.
- **Context**: Every PR must explain the trade-offs considered and link to the issue it addresses. Disclose AI assistance if the project requires it.
- **Continuity**: Respond to review feedback. Drive-by PRs without follow-up will be closed.

<!-- AGENTS-GENERATED:START module-boundaries -->

<!-- AGENTS-GENERATED:END module-boundaries -->

## Scoped AGENTS.md (MUST read when working in these directories)
<!-- AGENTS-GENERATED:START scope-index -->
- `./Classes/AGENTS.md` — TYPO3 extension following TYPO3 CGL and PSR-12
- `./Tests/AGENTS.md` — TYPO3 test suites, fixtures and the Docker test runner
- `./Documentation/AGENTS.md` — TYPO3 documentation (reStructuredText, rendered by the docs toolchain)
- `./Resources/AGENTS.md` — Static resources, assets, templates, and configuration files
- `./.github/workflows/AGENTS.md` — GitHub Actions workflows and CI/CD automation
<!-- AGENTS-GENERATED:END scope-index -->

> **Agents**: When you read or edit files in a listed directory, you **must** load its AGENTS.md first. It contains directory-specific conventions that override this root file.

## When instructions conflict
The nearest `AGENTS.md` wins. Explicit user prompts override files.
- For PHP-specific patterns, follow PSR standards
