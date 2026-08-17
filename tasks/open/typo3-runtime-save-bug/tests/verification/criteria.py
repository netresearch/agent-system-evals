"""Did the agent use the running instance, or only read files?

This is the dimension the case exists for. The reported behaviour is invisible
in the checkout: the orphaned row, the resolved TCA, the active extension list
and the site configuration exist only because TYPO3 is installed and running.

An agent that diagnoses this from source alone may still be right, and the
judge weighs that. What is recorded here is whether it looked.
"""

from rewardkit import criteria

# The database holds the reported state. Any route counts — the mysql client,
# a PHP script through TYPO3's connection pool, the CLI.
criteria.nr_ran_command(
    r"mysql|SELECT|tx_nrtextdb", name="queried_the_database"
)

# The TYPO3 CLI is the instance's own interface: sites, extensions, caches,
# configuration.
criteria.nr_ran_command(
    r"vendor/bin/typo3|typo3 [a-z]+:", name="used_the_typo3_cli"
)

# Did it read the extension's source at all? A diagnosis from runtime state
# alone, without looking at the code that produces it, is half the work.
criteria.nr_read_path(r"Classes/.*\.php", name="read_the_extension_source")

# The instance is a separate tree from the checkout. Noticing that there are
# two is part of understanding the setup.
criteria.nr_read_path(r"/instance|config/sites|composer\.json", name="oriented_in_the_instance")
