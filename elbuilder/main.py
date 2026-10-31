from typing import Optional

import typer

from elbuilder.commands import (
    doctor_command,
    install_command,
    versions_command,
    setup_command,
    use_command,
    installed_command,
)
from elbuilder.core.config import ElBuilderConfig

app = typer.Typer()

config = ElBuilderConfig.make()


@app.command()
def doctor() -> None:
    """Validates the system environment to compile the php-src."""
    doctor_command()


@app.command()
def versions() -> None:
    """Show available versions."""
    versions_command()


@app.command()
def installed() -> None:
    """List installed builds (version + tags)."""
    installed_command()


@app.command()
def use(version: str) -> None:
    """Print export statements (PATH, plus a build's recorded runtime env) for the current shell.

    Args:
        version: a build id (e.g. '8.3.22+zts+asan'), or a bare version when only one build of it exists.

    Example:
        eval "$(elbuilder use 8.3.22+asan)"
    """
    use_command(version)


@app.command()
def install(
    version: str,
    flags: Optional[list[str]] = typer.Argument(None, help="Raw ./configure args, after --"),
    show_flags: bool = typer.Option(False, "--show-flags", help="Show available ./configure flags for this version"),
) -> None:
    """Install a PHP build.

    The version token carries elbuilder build tags via '+':
      threading  +nts (default) | +zts
      optim      +release (default) | +debug
      sanitizer  +none (default) | +asan | +ubsan
    Defaults (nts/release/none) normalize away, so '8.3.22+nts+asan' == '8.3.22+asan'.

    Anything after '--' is passed verbatim to ./configure (opaque; it only
    contributes a hash to the build id, it is never parsed as a tag).

    Examples:
        elbuilder install 8.3.22+zts+debug -- disable-all enable-cli with-libxml with-curl
        elbuilder install 8.3.22+asan      -- disable-all enable-cli with-libxml with-curl
    """
    install_command(version, flags, show_flags)


@app.command()
def setup() -> None:
    """Sets up elbuilder by adding shims to .bashrc/.zshrc."""
    setup_command()
