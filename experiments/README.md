# Experiment records

One JSON file per `scripts/run-comparison` invocation: the case, the arms, the
randomisation seed, the size and shuffled order of each stage, the jobs each
stage produced, how many trials were actually spent and why the run stopped.

It exists because none of that was recoverable afterwards. The seed lived only
in the command line, the stage structure only in the terminal scrollback, and a
run that stopped early looked identical to one that had never deepened. A
comparison whose stopping rule cannot be reconstructed is not reproducible even
in principle, whatever its jobs contain.

Committed rather than ignored, unlike `jobs/`: these are small, they carry no
credentials, and they are the part of a measurement that says how it was taken.
