from rich.console import Console
from rich.table import Table

from elbuilder.core.config import ElBuilderConfig
from elbuilder.core.source_manager import SourceManager
from elbuilder.core.release_manager import ReleaseManager


def versions_command() -> None:
    config = ElBuilderConfig.make()
    source_manager = SourceManager(config)
    manager = ReleaseManager(source_manager)
    latest_releases = manager.find_latest_releases("8")
    table = Table(title="Versions")
    table.add_column("Minor", style="cyan", no_wrap=True)
    table.add_column("Version", style="cyan", no_wrap=True)
    table.add_column("Channel", style="magenta")
    for minor in sorted(latest_releases.keys(), key=lambda x: list(map(int, x.split("."))), reverse=True):
        v = latest_releases[minor]
        table.add_row(minor, v.version, v.channel)
    Console().print(table)