# Changelog

All notable changes to this repository are documented here.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) · Versioning: [SemVer](https://semver.org/).

## [Unreleased]

Nothing yet. This release is feature-frozen for release-candidate validation.

## [0.1.0-rc.1] - 2026-09-30

First release candidate. Feature-frozen for Independent UAT. No new capabilities are
accepted in this cycle except blocker, contract, or QuickStart-completion fixes.

### Added — six user-visible Skills

- **Research** — evidence-bounded need/topic signal discovery from user-supplied local
  sources, with source/evidence references and a fixed `status=proposed` result. Optional.
- **Topic Planning** — generates comparable candidate topics from the Account Profile and
  goal, then compiles exactly one approved candidate into a Task Card.
- **Keyword** — matches query intent, proposes one main and several secondary terms,
  plans title/body/topic/tag placement, and emits a validated Keyword Plan.
- **Writing** — turns an approved Task Card, an approved Keyword Plan and the Account
  Profile into a structured draft (`status=draft`), preserving locked keywords verbatim.
- **Visual** — consumes only human-approved, hash-verified writing and renders eight
  offline SVG pages plus QA and a Production Manifest. No image API required.
- **Learning** — compares draft vs. approved final and emits evidence-linked, human-gated
  rule proposals. Side loop; never writes back to rules automatically.

### Added — infrastructure

- **Provider-agnostic Production Path** — the host Agent performs inference; the repo
  defines context, instructions, contracts, validators and human gates. No bundled API.
- **Contracts** — 13 Draft 2020-12 JSON Schemas (Task Card, Note Type, Keyword Plan,
  Finalization, Visual Output, Account Profile, Topic Planning Result, Writing Result,
  Production Manifest, Research Request/Result, Learning Feedback/Review).
- **Validators** — dependency-free validators for Task Card, Keyword Plan, Writing,
  Finalization, Visual Output, Research Result and Learning Review.
- **Visual SVG Renderer** — `scripts/render_visual.py` renders eight dynamic, offline
  SVG pages from an approved Writing Result. No external images or fonts.
- **Research Local Mode** — `scripts/run_research.py` + local JSON/CSV/Markdown source
  adapter. Offline; no scraping, no credentials.
- **Learning Review** — `scripts/run_learning_review.py` and
  `scripts/record_learning_decision.py` (proposal-only, record-only decision).
- **Starter Preset** — `presets/starter/*` copyable configuration templates.
- **`init_project.py`** — creates a user-owned `config/ workspace/ outputs/ learning/`
  tree and refuses to overwrite an existing destination.
- **QuickStart** — `docs/QUICKSTART.md` for a first run without editing source.
- **Documentation set** — README, USER_GUIDE, CUSTOMIZATION, ARCHITECTURE, CONTRACTS,
  TROUBLESHOOTING, QUICKSTART, DEPENDENCY audit, UAT and readiness reports.
- **LICENSE (MIT)** and **NOTICE.md** attribution and dependency/license record.
- **Regression tests** — 17 unit tests plus a contract harness, static synthetic
  smoke-check and deterministic end-to-end demo.

### Changed

- `docs/PUBLIC_DEPENDENCY_AUDIT.md` reclassified to the final release vocabulary
  (`SAFE_TO_DISTRIBUTE` / `SAFE_AS_DEPENDENCY` / `USER_PROVIDED` / `OPTIONAL_EXTERNAL` /
  `PRIVATE_ONLY`); no `UNKNOWN` entries remain.
- `.gitignore` extended to keep example fixtures tracked while excluding user runtime data.

### Security

- Private leak scan: 0 real secrets, credentials, IDs or absolute user paths.
- Private source tree, original Vault and migration records remain outside this repo.

### Notes

- `scripts/run_synthetic_demo.py` is a deterministic regression/demo executor, not an AI
  generation service; its approvals are explicitly named synthetic mocks.
- Cross-Agent behaviour and real audience content quality still require independent user
  acceptance testing; see `docs/INDEPENDENT_UAT_REPORT.md`.
