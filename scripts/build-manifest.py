#!/usr/bin/env python3
"""
Build manifest.json from the variant folders in this repo.

Schema:
{
  "schemaVersion": 3,
  "version": N,
  "updatedAt": "<UTC ISO-8601>",
  "repoSha": "<commit sha>",
  "notes": "<freeform>",
  "variants": {
    "AVariantLevel": {
      "totalLevels": K,
      "levels": { "1": "<sha256[0:12]>", ... }
    },
    "BVariantLevel": { ... }
  }
}

The Unity client compares per-file hashes against its cache and downloads only
the changed files. version monotonically increases each time this runs.
"""
import datetime
import hashlib
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VARIANT_FOLDERS = ["AVariantLevel", "BVariantLevel"]
MANIFEST_PATH = os.path.join(ROOT, "manifest.json")
LEVEL_RE = re.compile(r"^level_(\d+)\.json$")


def hash_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()[:12]


def build_variant(folder: str) -> dict:
    full = os.path.join(ROOT, folder)
    if not os.path.isdir(full):
        return {"totalLevels": 0, "levels": {}}
    levels: dict[str, str] = {}
    for name in os.listdir(full):
        m = LEVEL_RE.match(name)
        if not m:
            continue
        n = int(m.group(1))
        levels[str(n)] = hash_file(os.path.join(full, name))
    return {
        "totalLevels": len(levels),
        "levels": dict(sorted(levels.items(), key=lambda kv: int(kv[0]))),
    }


def previous_version() -> int:
    if not os.path.exists(MANIFEST_PATH):
        return 0
    try:
        with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
            return int(json.load(f).get("version", 0))
    except Exception:
        return 0


def main() -> int:
    repo_sha = os.environ.get("GITHUB_SHA", "").strip()
    if not repo_sha and len(sys.argv) > 1:
        repo_sha = sys.argv[1].strip()
    notes = os.environ.get("MANIFEST_NOTES", "").strip() or "Auto-generated"
    updated_at = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    next_version = previous_version() + 1

    variants = {folder: build_variant(folder) for folder in VARIANT_FOLDERS}

    manifest = {
        "schemaVersion": 3,
        "version": next_version,
        "updatedAt": updated_at,
        "repoSha": repo_sha,
        "notes": notes,
        "variants": variants,
    }

    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        f.write("\n")

    total = sum(v["totalLevels"] for v in variants.values())
    print(
        f"manifest v={next_version} sha={repo_sha[:8]} updatedAt={updated_at} "
        f"variants={len(variants)} totalFiles={total}"
    )
    for folder, v in variants.items():
        print(f"  {folder}: {v['totalLevels']} levels")
    return 0


if __name__ == "__main__":
    sys.exit(main())
