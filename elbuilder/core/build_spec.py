"""Build specifications: parse `version+tag+tag` selectors into configure
flags, compiler/runtime env, and a canonical, collision-free build id.

Two namespaces, no overlap:
  * `+tag`  in the version token -> known build dimensions, expanded here.
  * `--`    raw ./configure args -> opaque, passed through verbatim, and
            folded into the build id only as a hash (never parsed as tags).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

# Dimension order is also the order tags render in a canonical build id.
DIMENSIONS = ("threading", "optim", "sanitizer")


@dataclass(frozen=True)
class Tag:
    name: str
    dimension: str
    default: bool = False
    configure: tuple = ()                 # extra ./configure flags
    cflags: str = ""
    ldflags: str = ""
    runtime_env: Dict[str, str] = field(default_factory=dict)
    warns_with: frozenset = frozenset()   # soft-warn when combined with these


TAG_REGISTRY: Dict[str, Tag] = {
    # threading
    "nts": Tag("nts", "threading", default=True),
    "zts": Tag("zts", "threading", configure=("--enable-zts",)),
    # optimization / assertions
    "release": Tag("release", "optim", default=True),
    "debug": Tag("debug", "optim", configure=("--enable-debug",)),
    # sanitizers
    "none": Tag("none", "sanitizer", default=True),
    "asan": Tag(
        "asan", "sanitizer",
        # deliberately NO --enable-debug: the zend assert SIGABRTs before ASAN
        # ever sees the fault, so an asan build omits it.
        cflags="-fsanitize=address -fno-omit-frame-pointer -g -O0",
        ldflags="-fsanitize=address",
        runtime_env={
            "USE_ZEND_ALLOC": "0",  # route emalloc/efree to system malloc so ASAN sees it
            "ASAN_OPTIONS": "detect_leaks=0:abort_on_error=1:fast_unwind_on_malloc=0:symbolize=1",
        },
        warns_with=frozenset({"debug"}),
    ),
    "ubsan": Tag(
        "ubsan", "sanitizer",
        cflags="-fsanitize=undefined -fno-omit-frame-pointer -g",
        ldflags="-fsanitize=undefined",
        runtime_env={"UBSAN_OPTIONS": "print_stacktrace=1:halt_on_error=1"},
    ),
}

DEFAULTS: Dict[str, str] = {t.dimension: t.name for t in TAG_REGISTRY.values() if t.default}


class BuildSpecError(ValueError):
    """Raised for an unknown tag or a within-dimension conflict."""


@dataclass
class BuildSpec:
    version: str                       # git version, e.g. "8.3.22"
    tags: Dict[str, str]               # dimension -> chosen tag (defaults filled)
    raw_flags: List[str] = field(default_factory=list)       # opaque -- args (normalized to --)
    baseline_flags: List[str] = field(default_factory=list)  # from config.php_configure_flags

    # ---- parsing ---------------------------------------------------------
    @classmethod
    def parse(
        cls,
        selector: str,
        raw_flags: Optional[List[str]] = None,
        baseline_flags: Optional[List[str]] = None,
    ) -> "BuildSpec":
        parts = selector.split("+")
        version = parts[0].strip()
        if not version:
            raise BuildSpecError("missing version before '+' in selector")

        chosen: Dict[str, str] = {}
        for token in parts[1:]:
            name = token.strip().lower()
            if not name:
                continue
            tag = TAG_REGISTRY.get(name)
            if tag is None:
                raise BuildSpecError(
                    f"unknown tag '+{name}'. known tags: " + ", ".join(sorted(TAG_REGISTRY))
                )
            prev = chosen.get(tag.dimension)
            if prev is not None and prev != name:
                raise BuildSpecError(
                    f"conflicting {tag.dimension} tags: '+{prev}' and '+{name}'"
                )
            chosen[tag.dimension] = name

        tags = {dim: DEFAULTS[dim] for dim in DIMENSIONS}
        tags.update(chosen)
        return cls(
            version=version,
            tags=tags,
            raw_flags=list(raw_flags or []),
            baseline_flags=list(baseline_flags or []),
        )

    # ---- resolution ------------------------------------------------------
    def _active_tags(self) -> List[Tag]:
        return [TAG_REGISTRY[self.tags[d]] for d in DIMENSIONS]

    def non_default_tags(self) -> List[str]:
        """Chosen tags that differ from the dimension default (nts/release/none
        normalize away), in dimension order."""
        return [self.tags[d] for d in DIMENSIONS if self.tags[d] != DEFAULTS[d]]

    def configure_flags(self) -> List[str]:
        flags: List[str] = list(self.baseline_flags)
        for t in self._active_tags():
            flags.extend(t.configure)
        flags.extend(self.raw_flags)
        seen: set = set()
        out: List[str] = []
        for f in flags:
            if f not in seen:
                seen.add(f)
                out.append(f)
        return out

    def cflags(self) -> str:
        return " ".join(t.cflags for t in self._active_tags() if t.cflags).strip()

    def ldflags(self) -> str:
        return " ".join(t.ldflags for t in self._active_tags() if t.ldflags).strip()

    def runtime_env(self) -> Dict[str, str]:
        env: Dict[str, str] = {}
        for t in self._active_tags():
            env.update(t.runtime_env)
        return env

    def warnings(self) -> List[str]:
        out: List[str] = []
        active = set(self.non_default_tags())
        for t in self._active_tags():
            hit = t.warns_with & active
            if hit:
                joined = ", ".join(f"'+{h}'" for h in sorted(hit))
                out.append(f"'+{t.name}' is usually not combined with {joined}")
        return out

    # ---- identity --------------------------------------------------------
    def build_id(self) -> str:
        # Identity is version + non-default tags only. The raw ``--`` flags are
        # build *inputs*, not identity: reinstalling the same id with different
        # flags is a replace, guarded by the installer's "already installed"
        # check (and, later, --force).
        return "+".join([self.version, *self.non_default_tags()])

    # ---- manifest --------------------------------------------------------
    def manifest(self) -> Dict:
        return {
            "version": self.version,
            "tags": self.non_default_tags(),
            "build_id": self.build_id(),
            "configure_flags": self.configure_flags(),
            "cflags": self.cflags(),
            "ldflags": self.ldflags(),
            "runtime_env": self.runtime_env(),
            "raw_flags": self.raw_flags,
        }
