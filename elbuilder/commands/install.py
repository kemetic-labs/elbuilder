import subprocess
from typing import Optional

from elbuilder.core.config import ElBuilderConfig
from elbuilder.core.installer import Installer
from elbuilder.core.source_manager import SourceManager


def install_command(
    version: str,
    flags: Optional[list[str]] = None,
    show_flags: bool = False,
    config: ElBuilderConfig | None = None,
) -> None:
    config = config or ElBuilderConfig.make()
    sm = SourceManager(config=config)
    if flags is None:
        flags = []
    if show_flags:
        sm.ensure_src()
        sm.checkout(version)
        src_dir = config.src_dir
        try:
            print("Running buildconf to generate configure script...")
            subprocess.run(["./buildconf", "--force"], cwd=src_dir, check=True)  # noqa: S603
            
            out = subprocess.check_output(["./configure", "--help"], cwd=src_dir, text=True)  # noqa: S603
            print(out)
        except subprocess.CalledProcessError as e:
            print(f"Error: {e}")
        return


    processed_flags = []
    if flags:
        for flag in flags:
            if not flag.startswith("--"):
                processed_flags.append(f"--{flag}")
            else:
                processed_flags.append(flag)
    Installer(sm, config).install(version, processed_flags)
    print(f"\nTo use PHP {version} in your current shell, run:")
    print(f'  eval "$(elbuilder use {version})"')
