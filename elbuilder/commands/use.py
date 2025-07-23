from elbuilder.core.config import ElBuilderConfig
from elbuilder.core.exceptions import VersionNotFound


def use_command(version: str, config: ElBuilderConfig | None = None) -> None:
    config = config or ElBuilderConfig.make()
    install_dir = config.versions_dir / version
    if not install_dir.exists():
        raise VersionNotFound(
            f"PHP Version: {version} was not found, use elbuilder install, or check installed (elbuilder installed)")
    bin_dir = install_dir / "bin"
    shims_dir = config.shims_dir

    shims_dir.mkdir(exist_ok=True)
    for executable_name in ["php", "phpize", "php-config", "phar", "phpdbg", "php-cgi"]:
        src = bin_dir / executable_name
        dst = shims_dir / executable_name
        if src.exists():
            if dst.exists():
                dst.unlink()
            dst.symlink_to(src)

    print(f'export PATH="{shims_dir}:$PATH"')
