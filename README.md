# popsort-levels

Remote level content for **Popcorn Sort** (Unity, mobile). Consumed by the
Unity client at runtime via:

- **Manifest:** GitHub Contents API (instant, no ref cache)
  `https://api.github.com/repos/nihatcagri44/popsort-levels/contents/manifest.json`
- **Level files:** jsDelivr CDN, SHA-pinned for immutable URLs / instant cache invalidation
  `https://cdn.jsdelivr.net/gh/nihatcagri44/popsort-levels@<repoSha>/<folder>/level_NNN.json`

## Folder layout

```
popsort-levels/
├─ AVariantLevel/             # A/B test variant A
│   └─ level_001.json … level_030.json
├─ BVariantLevel/             # A/B test variant B
│   └─ level_001.json … level_030.json
├─ manifest.json              # auto-generated — DO NOT edit by hand
├─ scripts/build-manifest.py  # manifest generator
└─ .github/workflows/regenerate-manifest.yml
```

## How content flows

1. Designer edits levels in **DawnbrightGames/gamejam2** (`Assets/_GAME/Resources/{A,B}VariantLevel/`)
2. Tester verifies in Unity Editor, then triggers
   **gamejam2 → Actions → "Publish VariantLevels → popsort-levels"** (manual `workflow_dispatch`)
3. That workflow pushes the changed JSONs into this repo
4. **regenerate-manifest.yml** runs automatically → rebuilds `manifest.json`
   (new `version` + new `repoSha` + per-file `sha256[:12]`)
5. Unity clients pick up changes on next launch:
   - manifest fetch → diff vs. local cache → download only changed files
   - jsDelivr URL is SHA-pinned, so a new commit = a new URL = instant fresh content

## Manual regeneration

Use **Actions → Regenerate manifest.json → Run workflow** if you ever edit
levels directly in this repo (rare — source of truth is gamejam2).

## Manifest schema

```jsonc
{
  "schemaVersion": 3,
  "version": 7,                   // monotonically increasing
  "updatedAt": "2026-05-22T10:30:00Z",
  "repoSha": "abc1234…",          // pinned by client to build jsDelivr URLs
  "notes": "L12 difficulty fix",
  "variants": {
    "AVariantLevel": {
      "totalLevels": 30,
      "levels": { "1": "a1b2c3d4e5f6", "2": "…", ... }   // sha256[:12]
    },
    "BVariantLevel": { ... }
  }
}
```

## Unity client setup

See `gamejam2/docs/remote-levels-setup.md` for the full pipeline (PAT secret,
sync workflow, Firebase Remote Config wiring, AB suspend flag).
