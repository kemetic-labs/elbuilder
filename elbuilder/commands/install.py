import subprocess
from typing import Optional

from elbuilder.core.build_spec import BuildSpec, BuildSpecError
from elbuilder.core.config import ElBuilderConfig
from elbuilder.core.installer import Installer
from elbuilder.core.source_manager import SourceManager


def _normalize(flags: list[str]) -> list[str]:
    return [f if f.startswith("--") else f"--{f}" for f in flags]


def install_command(
    version: str,
    flags: Optional[list[str]] = None,
    show_flags: bool = False,
    config: ElBuilderConfig | None = None,
) -> None:
    config = config or ElBuilderConfig.make()
    sm = SourceManager(config=config)
    raw_flags = _normalize(flags or [])

    # The version token may carry +tags; configure --help only needs the tag.
    base_version = version.split("+", 1)[0]

    if show_flags:
        sm.ensure_src()
        sm.checkout(base_version)
        src_dir = config.src_dir
        try:
            print("Running buildconf to generate configure script...")
            subprocess.run(["./buildconf", "--force"], cwd=src_dir, check=True)  # noqa: S603
            out = subprocess.check_output(["./configure", "--help"], cwd=src_dir, text=True)  # noqa: S603
            print(out)
        except subprocess.CalledProcessError as e:
            print(f"Error: {e}")
        return

    baseline = _normalize((config.php_configure_flags or "").split())
    try:
        spec = BuildSpec.parse(version, raw_flags=raw_flags, baseline_flags=baseline)
    except BuildSpecError as e:
        print(f"Error: {e}")
        raise SystemExit(2)

    for w in spec.warnings():
        print(f"[elbuilder] warning: {w}")

    Installer(sm, config).install(spec)

    build_id = spec.build_id()
    print(f"\nTo use PHP build {build_id} in your current shell, run:")
    print(f'  eval "$(elbuilder use {build_id})"')
