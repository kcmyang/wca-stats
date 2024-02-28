# wca-stats

Scripts for working with WCA results exports, plus fun queries.

## Prerequisites

- MySQL

## Use

Run `scripts/setup-db.py` to update your results export.
This relies only on the `timestamp` file, which will be created/updated by the script.

## Todo

- [ ] Use `argparse` to pass magic values to the script
