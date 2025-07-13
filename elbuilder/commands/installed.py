from rich.console import Console
from rich.table import Table
from elbuilder.core.config import ElBuilderConfig

def installed_command(config: ElBuilderConfig | None = None) -> None:
    config = config or ElBuilderConfig.make()
    versions_dir = config.versions_dir
    if not versions_dir.exists():
        print("No PHP versions installed.")
        return
    versions = [d.name for d in versions_dir.iterdir() if d.is_dir()]
    if not versions:
        print("No PHP versions installed.")
        return
    table = Table(title="Installed PHP Versions")
    table.add_column("Version", style="cyan", no_wrap=True)
    table.add_column("Path", style="green")
    for v in sorted(versions, reverse=True):
        table.add_row(v, str(versions_dir / v))
    Console().print(table) 