"""Mechanical floor for verification.

The target ships PHPStan, Rector, PHP-CS-Fixer, phplint and PHPUnit, all
installed and exposed through Composer scripts and Makefile targets. So "the
tool was not available" is not an available explanation here, and whether each
was actually executed is decidable from the command log.

These criteria record execution only. Whether running a given tool was
*warranted* for this request is the judge's question — an agent that skips
Rector on a review request has not necessarily done anything wrong.
"""

from rewardkit import criteria

criteria.nr_ran_command(r"phpstan|ci:test:php:phpstan|make phpstan", name="ran_phpstan")
criteria.nr_ran_command(
    r"phpunit|ci:test:php:unit|make test", name="ran_test_suite"
)
criteria.nr_ran_command(
    r"php-cs-fixer|ci:test:php:cgl|make cgl", name="ran_code_style_check"
)

# Anything at all from the project's own entry points. Broader than the three
# above on purpose: an agent that found `make help` and worked from there has
# verified through the project's interface even if it chose different targets.
criteria.nr_ran_command(
    r"composer (ci:|run)|make [a-z]", name="used_project_entry_points"
)
