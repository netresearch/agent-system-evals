"""Did the agent check its own work, before being asked to?

The collect hooks run the result afterwards regardless — that is
outcome_quality. This dimension is about whether the agent verified during the
work, which is the difference between knowing the change is sound and hoping.

The project ships PHPStan, PHP-CS-Fixer, Fractor, PHPUnit with unit and
functional suites, PHPat and Infection, all exposed through Composer scripts
and a Makefile. Nothing here is unavailable.
"""

from rewardkit import criteria

criteria.nr_ran_command(r"phpunit|ci:test:php:unit|make test", name="ran_tests")
criteria.nr_ran_command(r"phpstan|ci:test:php:phpstan", name="ran_static_analysis")
criteria.nr_ran_command(
    r"composer (update|require|install)", name="installed_what_it_declared"
)

# Did it use the project's own entry points rather than inventing commands?
criteria.nr_ran_command(
    r"composer (ci:|run)|make [a-z]", name="used_project_entry_points"
)
