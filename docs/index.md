# elbuilder

[![Release](https://img.shields.io/github/v/release/kemetic-labs/elbuilder)](https://img.shields.io/github/v/release/kemetic-labs/elbuilder)
[![Build status](https://img.shields.io/github/actions/workflow/status/kemetic-labs/elbuilder/main.yml?branch=main)](https://github.com/kemetic-labs/elbuilder/actions/workflows/main.yml?query=branch%3Amain)
[![Commit activity](https://img.shields.io/github/commit-activity/m/kemetic-labs/elbuilder)](https://img.shields.io/github/commit-activity/m/kemetic-labs/elbuilder)
[![License](https://img.shields.io/github/license/kemetic-labs/elbuilder)](https://img.shields.io/github/license/kemetic-labs/elbuilder)

PHP Source Builder

## Quick Start

```bash
pipx install elbuilder
elbuilder doctor
elbuilder versions
elbuilder install 8.3.22
elbuilder setup
elbuilder use 8.3.22
```

## Commands

- `elbuilder doctor` - Verify build dependencies
- `elbuilder versions` - List available PHP versions
- `elbuilder install <version>` - Build and install PHP version
- `elbuilder installed` - List installed versions
- `elbuilder use <version>` - Switch active PHP version
- `elbuilder setup` - Configure shell integration

## Tutorial

See [Tutorial](tutorial.md) for complete multi-version setup walkthrough.
