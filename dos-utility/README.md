# DOS-Utility

This is a package shared with multiple services, which provides different general purpose functions/classes.<br>
You can install it in a service with this command:

```bash
uv add <relative-path>/dos-utility
```

## Prerequisites

In order to work locally with this package you need the following tools:

- uv
- [task](https://taskfile.dev/)

## Unit test

Run unit tests with coverage report, no threshold enforced:

```bash
task test:quick
```

Run unit tests enforcing a minimum coverage threshold (default: 80%):

```bash
task test
```

To override the minimum coverage threshold:

```bash
task test COV_THREASHOLD=90
```

If you implement a feature add unit tests and make sure the coverage is as close as possible to 100%.

## Features

If you want to know what kind of features this package provides, checkout [this](./docs/features.md) page.