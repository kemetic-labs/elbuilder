import json
import re
from pathlib import Path

from rich.console import Console
from rich.table import Table

from elbuilder.core.config import ElBuilderConfig

_HASH_SUFFIX = re.compile(r"\.[0-9a-f]{8}$")


def _version_of(d: Path) -> str:
    manifest = d / "build.json"
    if manifest.exists():
        try:
            v = json.loads(manifest.read_text()).get("version")
            if v:
                return v
        except (ValueError, OSError):
            pass
    name = d.name.split("+", 1)[0]
    return _HASH_SUFFIX.sub("", name)


def _tags_of(d: Path) -> str:
    manifest = d / "build.json"
    if manifest.exists():
        try:
            tags = json.loads(manifest.read_text()).get("tags") or []
            return "+".join(tags) if tags else "-"
        except (ValueError, OSError):
            pass
    if "+" in d.name:
        rest = d.name.split("+", 1)[1]
        return _HASH_SUFFIX.sub("", rest) or "-"
    return "-"


def installed_command(config: ElBuilderConfig | None = None) -> None:
    config = config or ElBuilderConfig.make()
    versions_dir = config.versions_dir
    dirs = [d for d in versions_dir.iterdir() if d.is_dir()] if versions_dir.exists() else []
    if not dirs:
        print("No PHP versions installed.")
        return
    table = Table(title="Installed PHP Builds")
    table.add_column("Build", style="cyan", no_wrap=True)
    table.add_column("Version", style="cyan")
    table.add_column("Tags", style="magenta")
    table.add_column("Path", style="green")
    for d in sorted(dirs, key=lambda p: p.name, reverse=True):
        table.add_row(d.name, _version_of(d), _tags_of(d), str(d))
    Console().print(table)
