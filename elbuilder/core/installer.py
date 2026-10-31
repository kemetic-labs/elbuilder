from pathlib import Path
import json
import multiprocessing
import os
import subprocess
import time
from typing import Optional

from elbuilder.core.build_spec import BuildSpec
from elbuilder.core.config import ElBuilderConfig
from elbuilder.core.source_manager import SourceManager


class Installer:
    def __init__(self, source_manager: SourceManager, config: ElBuilderConfig):
        self.source_manager = source_manager
        self.config = config

    def install(self, spec: BuildSpec) -> Optional[Path]:
        versions_dir = self.config.versions_dir
        install_dir = versions_dir / spec.build_id()
        if not self.create_version_dir(install_dir):
            return None

        self.source_manager.ensure_src()
        self.source_manager.checkout(spec.version)
        versions_dir.mkdir(exist_ok=True)

        src_dir = self.config.src_dir
        subprocess.run(["./buildconf", "--force"], cwd=src_dir, check=True)  # noqa: S603

        # Real clean. Stale .o files from a previous build with different flags
        # (e.g. a non-ASAN build) would otherwise survive a reconfigure and
        # silently poison this one. buildconf+configure regenerate anyway.
        if (src_dir / "Makefile").exists():
            print("[elbuilder] make distclean (clearing previous build objects)...")
            subprocess.run(["make", "distclean"], cwd=src_dir, check=False)  # noqa: S603,S607

        env = self._build_env(spec)
        configure = ["./configure", f"--prefix={install_dir}", *spec.configure_flags()]
        print("[elbuilder] configure:", " ".join(configure))
        if env.get("CFLAGS"):
            print("[elbuilder] CFLAGS:", env["CFLAGS"])
        if env.get("LDFLAGS"):
            print("[elbuilder] LDFLAGS:", env["LDFLAGS"])
        subprocess.run(configure, cwd=src_dir, check=True, env=env)  # noqa: S603

        jobs = str(multiprocessing.cpu_count())
        subprocess.run(["make", f"-j{jobs}"], cwd=src_dir, check=True, env=env)  # noqa: S603,S607
        subprocess.run(["make", "install"], cwd=src_dir, check=True, env=env)  # noqa: S603,S607

        self._write_manifest(install_dir, spec)
        self._link_shims(install_dir)
        return install_dir

    def _build_env(self, spec: BuildSpec) -> dict:
        """Inherit the caller's env and append the spec's sanitizer flags, so a
        user-exported CFLAGS/LDFLAGS and a tag's flags compose rather than clobber."""
        env = dict(os.environ)
        cflags = " ".join(x for x in (env.get("CFLAGS", ""), spec.cflags()) if x).strip()
        ldflags = " ".join(x for x in (env.get("LDFLAGS", ""), spec.ldflags()) if x).strip()
        if cflags:
            env["CFLAGS"] = cflags
        if ldflags:
            env["LDFLAGS"] = ldflags
        return env

    def _write_manifest(self, install_dir: Path, spec: BuildSpec) -> None:
        data = spec.manifest()
        data["built_at"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
        (install_dir / "build.json").write_text(json.dumps(data, indent=2))

    def _link_shims(self, install_dir: Path) -> None:
        bin_dir = install_dir / "bin"
        shims_dir = self.config.shims_dir
        shims_dir.mkdir(exist_ok=True)
        for name in ["php", "phpize", "php-config", "phar", "phpdbg", "php-cgi"]:
            src = bin_dir / name
            dst = shims_dir / name
            if src.exists():
                if dst.exists() or dst.is_symlink():
                    dst.unlink()
                dst.symlink_to(src)

    @staticmethod
    def _is_complete(install_dir: Path) -> bool:
        """A build counts as installed only if it finished: a dir alone can be a
        leftover from an interrupted/failed build and must not block a reinstall."""
        return (install_dir / "build.json").exists() or (install_dir / "bin" / "php").exists()

    def create_version_dir(self, install_dir: Path) -> bool:
        if install_dir.exists() and self._is_complete(install_dir):
            print(f"Build {install_dir.name} is already installed.")
            return False
        if install_dir.exists():
            print(f"[elbuilder] {install_dir.name} exists but looks incomplete — rebuilding.")
        try:
            install_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            raise RuntimeError(f"Failed to create {install_dir}: {e}") from e
        return True
