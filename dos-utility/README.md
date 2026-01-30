# DOS-Utility

This is a package shared with multiple services, which provides different general purpose functions/classes.<br>
You can install it in a service with this command:

```bash
uv add <relative-path>/dos-utility
```

## Prerequisites

In order to work locally with this package you need the following tools:

- uv

## Unit test

To run test, run the following command:

```bash
uv run pytest --cov=dos_utility --cov-report=term-missing
```

If you implement a feature add unit tests and make sure the coverage is as close as possible to 100%.

## Features

If you want to know what kind of features this package provides, checkout [this](./docs/features.md) page.