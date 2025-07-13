from collections import defaultdict
from dataclasses import dataclass
from typing import List, Dict

from elbuilder.core.source_manager import SourceManager

@dataclass(frozen=True)
class Release:
    version: str
    date: str
    channel: str

class ReleaseManager:
    def __init__(self, source_manager: SourceManager):
        self.source_manager = source_manager

    def find_all_releases(self) -> List[Release]:
        result: List[Release] = []
        tag_tuples = self.source_manager.get_tags()
        for tag, date in tag_tuples:
            v = tag.replace("php-", "")
            channel = self.detect_channel(v)
            result.append(Release(version=v, date=date, channel=channel))
        return result

    def find_latest_releases(self, major: str = "8") -> Dict[str, Release]:
        releases = self.find_all_releases()
        grouped = self._group_by_minor(releases)
        grouped = {k: v for k, v in grouped.items() if k.startswith(f"{major}.")}
        return self._latest_patch_per_minor(grouped)

    @staticmethod
    def detect_channel(version: str) -> str:
        v = version.lower()
        if "rc" in v:
            return "RC"
        if "beta" in v:
            return "Beta"
        if "alpha" in v:
            return "Alpha"
        return "Stable"

    def _group_by_minor(self, releases: List[Release]) -> Dict[str, List[Release]]:
        grouped: Dict[str, List[Release]] = defaultdict(list)
        for r in releases:
            parts = r.version.split(".")
            if len(parts) < 2 or not all(part.isdigit() for part in parts):
                continue
            minor_key = f"{parts[0]}.{parts[1]}"
            grouped[minor_key].append(r)
        return grouped

    def _latest_patch_per_minor(self, grouped: Dict[str, List[Release]]) -> Dict[str, Release]:
        result: Dict[str, Release] = {}
        for minor_version, releases in grouped.items():
            latest = max(releases, key=lambda r: tuple(int(p) for p in r.version.split(".")))
            result[minor_version] = latest
        return result
