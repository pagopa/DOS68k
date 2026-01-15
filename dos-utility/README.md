# DOS-Utility

This is a package shared with multiple services, which provides different general purpose functions/classes.

## Prerequisites

In order to work locally with this package you need the following tools:

- uv

## Unit test

To run test, run the following command:

```bash
uv run pytest --cov=dos_utility --cov-report=term-missing
```

If you implement a feature add unit tests and make sure the coverage is as close as possible to 100%.