import subprocess
from typing import List, Optional, Callable, Any, Tuple
from elbuilder.core.config import ElBuilderConfig

class SourceManager:
    def __init__(
        self,
        config: ElBuilderConfig,
        run_cmd: Optional[Callable[..., subprocess.CompletedProcess[Any]]] = None,
        check_output: Optional[Callable[..., str]] = None,
    ):
        self.config = config
        self.run_cmd = run_cmd or subprocess.run
        self.check_output = check_output or subprocess.check_output

    def ensure_src(self) -> None:
        """Ensure the PHP source repository exists."""
        if not self.config.src_dir.exists():
            print(f"Cloning PHP source to {self.config.src_dir}")
            self.config.src_dir.parent.mkdir(parents=True, exist_ok=True)
            self.run_cmd([
                "git", "clone", "https://github.com/php/php-src.git",
                str(self.config.src_dir)
            ], check=True)
        else:
            # Update existing repository
            self.run_cmd(["git", "fetch", "--tags"], cwd=self.config.src_dir, check=True)

    def get_tags(self) -> List[Tuple[str, str]]:
        """Get tags from git repository."""
        self.ensure_src()
        result: List[Tuple[str, str]] = []
        try:
            out = self.check_output(["git", "tag", "--sort=-v:refname"], cwd=self.config.src_dir, text=True)
        except subprocess.CalledProcessError:
            return result

        for line in out.strip().splitlines():
            if not line.strip():
                continue
            tag = line.strip()
            result.append((tag, ""))
        return result

    def checkout(self, tag: str) -> None:
        """Checkout a specific git tag.

        Args:
            tag: Version tag (e.g., '8.3.22'). Will be prefixed with 'php-' if not already.
        """
        git_tag = tag if tag.startswith('php-') else f"php-{tag}"
        self.run_cmd(["git", "checkout", git_tag], cwd=self.config.src_dir, check=True)
