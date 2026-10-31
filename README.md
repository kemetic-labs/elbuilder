# elbuilder: A PHP builder

[![Release](https://img.shields.io/github/v/release/kemetic-labs/elbuilder)](https://img.shields.io/github/v/release/kemetic-labs/elbuilder)
[![Build status](https://img.shields.io/github/actions/workflow/status/kemetic-labs/elbuilder/main.yml?branch=main)](https://github.com/kemetic-labs/elbuilder/actions/workflows/main.yml?query=branch%3Amain)
[![codecov](https://codecov.io/gh/kemetic-labs/elbuilder/branch/main/graph/badge.svg)](https://codecov.io/gh/kemetic-labs/elbuilder)
[![License](https://img.shields.io/github/license/kemetic-labs/elbuilder)](https://img.shields.io/github/license/kemetic-labs/elbuilder)

A simple cli tool to help build, and switch between different PHP versions on the fly, mainly to simplify testing during extension development, but also can be a version manager.

## Features
- Verify build dependencies (tested on OSx and linux)
- Easily switch between php versions
- Minimal dependencies.

## Roadmap

- [x] **Core:** Build Flag Discovery (`--show-flags`)
- [x] **CLI:** `elbuilder doctor`
- [x] **CLI:** `elbuilder install <VERSION> -- <build_args>`
- [x] **CLI:** `elbuilder setup` (shell integration - shims)
- [x] **CLI:** `elbuilder versions`
- [x] **CLI:** `elbuilder installed`
- [x] **CLI:** `elbuilder use <VERSION>`
- [x] **CLI:** build tags — `install <VERSION>+<tag>...`
- [ ] **CLI:** `elbuilder default <VERSION>`
- [ ] **CLI:** `elbuilder update`



## Getting Started

### 1. Installation

For detailed instructions on installing prerequisites and `elbuilder` itself, please see the **[Installation Guide (INSTALL.md)](INSTALL.md)**.

### 2. Basic Usage

Once installed, you can manage PHP versions as follows:

```sh
# 1. list available versions
elbuilder versions

# 2. install a PHP version (any git tag will work)
elbuilder install 8.3.8

# 3. load in the current shell / switch to another installed version
elbuilder use 8.3.8

# 4. verify
php -v
```

### 3. Build tags

Install the same version multiple ways with `+tags`; raw `./configure` args still go after `--`:

```sh
# ZTS + debug
elbuilder install 8.3.22+zts+debug -- disable-all enable-cli with-libxml with-curl

# ASAN (sets USE_ZEND_ALLOC=0 / ASAN_OPTIONS automatically on `use`)
elbuilder install 8.3.22+asan -- disable-all enable-cli with-libxml with-curl
eval "$(elbuilder use 8.3.22+asan)"
```

Tags: threading `+nts`/`+zts`, optim `+release`/`+debug`, sanitizer `+none`/`+asan`/`+ubsan`.
Defaults (`nts`/`release`/`none`) are implied, so `8.3.22+asan` == `8.3.22+nts+asan`.

For more real-world usage examples, see:
- [Simple PHP Setup](recipes/1_simple_setup.md)
- [Minimal PHP CLI](recipes/2_minimal_php_cli.md)
- [PHP with Debug and ZTS](recipes/3_php_debug_zts.md)
- [All Recipes](recipes/)
