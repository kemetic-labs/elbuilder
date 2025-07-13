from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings


class ElBuilderConfig(BaseSettings):
    home_dir: Path
    elbuilder_dir: Path
    src_dir: Path
    versions_dir: Path
    shims_dir: Path
    php_configure_flags: Optional[str] = None
    build_jobs: int = 4

    class Config:
        env_prefix = "ELB_"
        arbitrary_types_allowed = True

    @classmethod
    def make(cls, from_dir: Optional[Path] = None) -> "ElBuilderConfig":
        """Create an ElBuilderConfig instance with default directory structure.
        
        Args:
            from_dir: Base directory (typically user's home directory)
            
        Returns:
            ElBuilderConfig
        """
        home: Path = from_dir or Path.home()
        elbuilder_dir: Path = home / ".elbuilder"
        src_dir: Path = elbuilder_dir / "php-src"
        versions_dir: Path = elbuilder_dir / "versions"
        shims_dir: Path = elbuilder_dir / "shims"
        
        return cls(
            home_dir=home,
            elbuilder_dir=elbuilder_dir,
            src_dir=src_dir,
            versions_dir=versions_dir,
            shims_dir=shims_dir
        )
