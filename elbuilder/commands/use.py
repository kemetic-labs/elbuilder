import json
from pathlib import Path
from typing import Optional

from elbuilder.core.config import ElBuilderConfig
from elbuilder.core.exceptions import VersionNotFound


def _resolve_build(versions_dir: Path, selector: str) -> Optional[Path]:
    exact = versions_dir / selector
    if exact.exists():
        return exact
    if not versions_dir.exists():
        return None
    # Bare version given: match any build of it, disambiguate if more than one.
    candidates = sorted(
        d for d in versions_dir.iterdir()
        if d.is_dir() and (
            d.name == selector
            or d.name.startswith(selector + "+")
            or d.name.startswith(selector + ".")
        )
    )
    if len(candidates) == 1:
        return candidates[0]
    if len(candidates) > 1:
        names = ", ".join(c.name for c in candidates)
        raise VersionNotFound(
            f"'{selector}' is ambiguous — installed builds: {names}. "
            f"Pass the full id, e.g. 'elbuilder use {candidates[0].name}'."
        )
    return None


def use_command(version: str, config: ElBuilderConfig | None = None) -> None:
    config = config or ElBuilderConfig.make()
    install_dir = _resolve_build(config.versions_dir, version)
    if install_dir is None:
        raise VersionNotFound(
            f"PHP build '{version}' was not found. Run 'elbuilder install {version}' "
            f"or list builds with 'elbuilder installed'."
        )

    bin_dir = install_dir / "bin"
    shims_dir = config.shims_dir
    shims_dir.mkdir(exist_ok=True)
    for name in ["php", "phpize", "php-config", "phar", "phpdbg", "php-cgi"]:
        src = bin_dir / name
        dst = shims_dir / name
        if src.exists():
            if dst.exists() or dst.is_symlink():
                dst.unlink()
            dst.symlink_to(src)

    print(f'export PATH="{shims_dir}:$PATH"')

    # Emit any runtime env recorded for this build (e.g. ASAN_OPTIONS,
    # USE_ZEND_ALLOC) so activating an asan build sets it automatically.
    manifest = install_dir / "build.json"
    if manifest.exists():
        try:
            data = json.loads(manifest.read_text())
        except (ValueError, OSError):
            data = {}
        for key, val in (data.get("runtime_env") or {}).items():
            print(f'export {key}="{val}"')
