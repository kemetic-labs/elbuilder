from typing import Optional

import typer

from elbuilder.commands import doctor_command, install_command, versions_command, setup_command, use_command, installed_command
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
    """List installed versions."""
    installed_command()


@app.command()
def use(version: str) -> None:
    """Just Prints an export statement (PATH prepend) to use in the current shell.
    
    Args:
        version: PHP version to install (e.g., '8.3.22')
        
    Example:
        elbuilder use 8.3.22
"""
    use_command(version)


@app.command()
def install(
    version: str,
    flags: Optional[list[str]] = typer.Argument(None, help="Build flags to pass to configure"),
    show_flags: bool = typer.Option(False, "--show-flags", help="Show available build flags for this PHP version"),
) -> None:
    """Install a specific PHP version with optional build flags.
    
    Args:
        version: PHP version to install (e.g., '8.3.22')
        flags: Optional build flags to pass to configure
        
    Example:
        elbuilder install 8.3.22 -- disable-all enable-cli with-libxml with-curl
"""
    install_command(version, flags, show_flags)


@app.command()
def setup() -> None:
    """Sets up elbuilder by adding shims to .bashrc/.zshrc."""
    setup_command()

