from pathlib import Path
import multiprocessing
import subprocess

from elbuilder.core.config import ElBuilderConfig
from elbuilder.core.source_manager import SourceManager


class Installer:
    def __init__(self, source_manager: SourceManager, config: ElBuilderConfig):
        self.source_manager = source_manager
        self.config = config

    def install(self, version: str, flags: list[str]) -> None:
        src_dir = self.config.src_dir
        versions_dir = self.config.versions_dir
        install_dir = versions_dir / version
        if not self.create_version_dir(install_dir):
            return

        self.source_manager.ensure_src()
        self.source_manager.checkout(version)
        versions_dir.mkdir(exist_ok=True)
        subprocess.run(["./buildconf", "--force"], cwd=src_dir, check=True)  # noqa: S603
        print("[elbuilder] Running 'make clean' before build...")
        configure = ["./configure", f"--prefix={install_dir}", *flags]
        subprocess.run(configure, cwd=src_dir, check=True)  # noqa: S603
        jobs = str(multiprocessing.cpu_count())
        subprocess.run(["make", f"-j{jobs}"], cwd=src_dir, check=True)  # noqa: S603, S607
        subprocess.run(["make", "install"], cwd=src_dir, check=True)  # noqa: S603, S607
        bin_dir = install_dir / "bin"
        shims_dir = self.config.shims_dir
        shims_dir.mkdir(exist_ok=True)
        for executable_name in ["php", "phpize", "php-config", "phar", "phpdbg", "php-cgi"]:
            src = bin_dir / executable_name
            dst = shims_dir / executable_name
            if src.exists():
                if dst.exists():
                    dst.unlink()
                dst.symlink_to(src)
    def create_version_dir(self, install_dir: Path) -> bool:
        if not install_dir.exists():
            try:
                install_dir.mkdir(parents=True, exist_ok=True)
            except OSError as e:
                raise RuntimeError(f"Failed to create {install_dir}: {e}") from e
        else:
            print(f"PHP version {install_dir.name} is already installed.")
            return False
        return True
