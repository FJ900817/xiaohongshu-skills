# NOTICE

This repository is distributed under the MIT License (see [`LICENSE`](LICENSE)).

This file records the attribution, licensing and third-party/dependency position of the
release candidate `0.1.0-rc.1`. It is the authoritative record for "can this ship?".

## Final classification vocabulary

Every component is classified as exactly one of:

- **SAFE_TO_DISTRIBUTE** — original content authored for this repository; may be redistributed under this repo's MIT license.
- **SAFE_AS_DEPENDENCY** — a specification or standard reference; no third-party code is bundled.
- **USER_PROVIDED** — the user supplies it at runtime; it is never shipped in this repository.
- **OPTIONAL_EXTERNAL** — an optional external service/integration the user may enable; nothing is bundled or called by default.
- **PRIVATE_ONLY** — must never enter this repository or any public export.

There is **no `UNKNOWN` and no `REPLACE_REQUIRED`** entry in the final release. Anything that
previously required replacement was either re-implemented as original content or removed, and
is not shipped.

## Component inventory

| Component | Where | Fact | Final classification |
|---|---|---|---|
| Python core (scripts / validators / engines) | `scripts/`, `validators/`, `skills/*/engine.py` | Original code, Python standard library only | SAFE_TO_DISTRIBUTE |
| Local research adapter | `adapters/research/local_json_source.py` | Original, stdlib-only, offline | SAFE_TO_DISTRIBUTE |
| JSON Schema contracts | `contracts/*.schema.json` | Original schemas; reference the JSON Schema 2020-12 specification | SAFE_TO_DISTRIBUTE |
| JSON Schema specification | `$schema` URI in `contracts/*` | Standard specification reference; no code bundled | SAFE_AS_DEPENDENCY |
| Validators | `validators/*.py` | Original, stdlib-only | SAFE_TO_DISTRIBUTE |
| SVG renderer | `scripts/render_visual.py` | Original generator; output is inline geometry + text | SAFE_TO_DISTRIBUTE |
| Starter presets | `presets/starter/*` | Original templates | SAFE_TO_DISTRIBUTE |
| Synthetic demo content | `examples/synthetic/**` | Authored synthetic fixtures; marked `synthetic` | SAFE_TO_DISTRIBUTE |
| First-run example output | `examples/first-run/**` | Synthetic SVG/JSON produced by this repo's renderer | SAFE_TO_DISTRIBUTE |
| Documentation | `README.md`, `docs/**` | Original text | SAFE_TO_DISTRIBUTE |
| Fonts | `presets/starter/visual-config.yaml` | **No font files are bundled.** Renders use the environment's system font stack (`Arial`, `Noto Sans CJK SC`, generic `sans-serif`) | USER_PROVIDED |
| Icons | `scripts/render_visual.py` | No icon library bundled; symbols are drawn as inline SVG geometry | SAFE_TO_DISTRIBUTE |
| Images / photos | entire repo | No photographic or third-party image binaries are included | — (none shipped) |
| Visual templates | repo | Self-authored generator, not copied from any external template | SAFE_TO_DISTRIBUTE |
| Third-party Python packages | repo | **None required at runtime** (standard library only); no vendored packages | — (none) |
| Node / npm packages | repo | **No `package.json` / lockfile**; no npm dependency | — (none) |
| Optional integrations (Feishu / Calendar / Platform) | `integrations/*` | Empty placeholder directories only; no implementation, no credentials, not called by default | OPTIONAL_EXTERNAL |
| Optional model / image provider | design | Not bundled; if a user wires one, they supply it | OPTIONAL_EXTERNAL |
| External documentation links | `README.md`, `CHANGELOG.md` | Links to keepachangelog.com, semver.org, json-schema.org — reference only, never fetched at runtime | OPTIONAL_EXTERNAL |
| User account profile / keyword catalog / config | `user-project/config/*` (user-created) | User runtime data; excluded by `.gitignore` | USER_PROVIDED |
| User source material for Research | user-supplied JSON/CSV/Markdown | User runtime data; never ships | USER_PROVIDED |
| Original account/business data, private prompt libraries, production cards, real metrics | outside repo | Retained in a separate private source area; never exported | PRIVATE_ONLY |

## Attribution

- No third-party code, font, image, icon or template is copied into this repository.
- Rendering relies only on the user's system fonts; the renderer degrades to a generic
  `sans-serif` stack when a preferred font is unavailable.
- Generated SVG pages contain only original geometry and text extracted from the user's own
  approved writing.

## Distribution note

Any future addition of a bundled font, image, icon set or third-party package must first be
recorded here with an explicit license and one of the final classifications above. Anything
that cannot be classified is treated as not distributable and is left out of the release.
