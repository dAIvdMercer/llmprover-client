"""GDrive operations + .meta.json provenance tracking."""
import json
import os
from datetime import datetime, timezone
from pathlib import Path


DRIVE_ROOT = "/content/drive/My Drive"


class DriveManager:
    def __init__(self, slug: str, folders: list = None):
        self.slug = slug
        self.root = Path(DRIVE_ROOT) / "pysolvr" / slug
        self.folders = folders or []

    def ensure_folders(self):
        """Create the pysolvr/{slug}/{folders} structure in GDrive."""
        self.root.mkdir(parents=True, exist_ok=True)
        for folder in self.folders:
            (self.root / folder).mkdir(parents=True, exist_ok=True)
        return str(self.root)

    def save(self, folder: str, filename: str, content: str, meta: dict = None) -> str:
        """Save a file + .meta.json companion. Returns the file path."""
        path = self.root / folder / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

        if meta:
            meta_path = path.with_suffix(path.suffix + ".meta.json")
            meta["timestamp"] = datetime.now(tz=timezone.utc).isoformat()
            meta["business_slug"] = self.slug
            meta_path.write_text(json.dumps(meta, indent=2, default=str), encoding="utf-8")

        return str(path)

    def load(self, folder: str, filename: str) -> tuple:
        """Load a file + its .meta.json. Returns (content, meta_dict)."""
        path = self.root / folder / filename
        if not path.exists():
            return None, None
        content = path.read_text(encoding="utf-8")
        meta_path = path.with_suffix(path.suffix + ".meta.json")
        meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
        return content, meta

    def list_files(self, folder: str) -> list:
        """List files in a folder with metadata summaries."""
        folder_path = self.root / folder
        if not folder_path.exists():
            return []
        results = []
        for f in sorted(folder_path.iterdir()):
            if f.is_file() and not f.name.endswith(".meta.json"):
                meta_path = f.with_suffix(f.suffix + ".meta.json")
                meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
                results.append({
                    "name": f.name,
                    "path": str(f),
                    "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
                    "meta": meta,
                })
        return results

    def get_history(self, folder: str) -> list:
        """Get provenance history from .meta.json files (for resumability)."""
        files = self.list_files(folder)
        return [{"file": f["name"], **f["meta"]} for f in files if f["meta"]]
