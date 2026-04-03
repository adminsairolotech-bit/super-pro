# super-pro

![npm](https://img.shields.io/npm/v/super-pro?label=npm%20version)
![license](https://img.shields.io/github/license/adminsairolotech-bit/super-pro)
![stars](https://img.shields.io/github/stars/adminsairolotech-bit/super-pro?style=social)

A production-ready meta-repository that unifies agent orchestration, reusable skills, UI/UX design-system automation, methodology-driven delivery workflows, and curated research/knowledge assets into one cohesive platform.  
`super-pro` combines the operational rigor of mature awesome-list automation with the execution power of multi-agent systems, making it ideal for teams that want to go from idea to validated output quickly and repeatably.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Why super-pro?](#why-super-pro)
- [Repository Architecture](#repository-architecture)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Detailed Usage](#detailed-usage)
  - [1) Run methodology-first project flow](#1-run-methodology-first-project-flow)
  - [2) Use modular skills with agent backends](#2-use-modular-skills-with-agent-backends)
  - [3) Design-system and brand token synchronization](#3-design-system-and-brand-token-synchronization)
  - [4) Curated resource ingestion and validation](#4-curated-resource-ingestion-and-validation)
  - [5) Second-brain knowledge workflows](#5-second-brain-knowledge-workflows)
  - [6) Prompt research, security, and red-team practices](#6-prompt-research-security-and-red-team-practices)
- [Configuration](#configuration)
- [CLI Reference](#cli-reference)
- [Quality, CI/CD, and Governance](#quality-cicd-and-governance)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)

---

## Overview

`super-pro` is a synthesized framework designed from seven complementary repositories to deliver:

- A scalable skill-and-agent operating model
- Cross-platform plugin compatibility
- UI/UX and brand automation pipelines
- Methodology-first software delivery orchestration
- Curated, validated knowledge and research operations

It is built for engineering teams, design teams, AI operators, and knowledge architects who need one system that is modular, auditable, and practical in real-world production.

---

## Features

- Unified multi-agent architecture with skill modules and backend-specific agent configs
- Methodology-first execution lifecycle:
  - spec -> plan -> execute -> review -> iterate
- Cross-tool interoperability (Buddy AI integrations)
- UI/UX and design-system toolkit:
  - brand extraction
  - token synchronization
  - asset validation
  - data-driven layout/color logic
- Repository-ops automation:
  - link validation
  - repo health checks
  - issue/PR submission enforcement
  - release and metadata update workflows
- Multi-view documentation generation for discoverability (A-Z, created, updated, releases)
- Structured contribution taxonomy for skills, agents, hooks, commands, and integrations
- Security-first and research-first operating posture
- Second-brain compatible knowledge capture and retrieval workflow patterns
- Prompt research corpus support for benchmarking, analysis, and red-team style evaluations
- Pre-commit and docs hygiene tooling for consistent contributions
- Extensible package/distribution design (npm-ready structure with plugin metadata)

---

## Why super-pro?

`super-pro` is not just a merge—it is a curated synthesis that addresses the limitations of each source while preserving their strongest patterns.

- Better than awesome-list-only repos: includes executable architecture, typed configuration, and runtime workflows—not just curated links.
- Better than skill-only repos: adds governance, CI health automation, discoverability tooling, and contribution pipelines.
- Better than agent-only repos: includes design-system, brand automation, and non-engineering workflows.
- Better than methodology-only repos: operationalizes methodology with reusable skills, command patterns, and plugin packaging.
- Better than prompt-collection-only repos: adds structured execution, validation, and security controls around prompt usage.
- Better than personal knowledge repos: introduces team-scale collaboration, automation, and policy guardrails.
- Better than hunting/checklist repos alone: integrates reconnaissance and analysis practices into a broader delivery and governance framework.

In short: `super-pro` provides execution depth, operational maturity, and multidisciplinary breadth in one coherent repository.

---

## Repository Architecture

Suggested top-level structure:

- `.agents/`
  - `skills/<skill-name>/SKILL.md`
  - `agents/<provider>.yaml`
- `.buddy-ai/skills/`
  - domain-specific skill packs (brand, design-system, research, etc.)
- `.plugins/`
  - buddy-ai plugin manifests and adapters
- `scripts/`
  - automation scripts (token sync, validation, ingestion, transforms)
- `data/`
  - CSV/JSON/YAML datasets for layout logic, prompt catalogs, and registries
- `.github/workflows/`
  - validation, moderation, health, release metadata automation
- `docs/`
  - generated index variants and usage playbooks
- `examples/`
  - runnable examples for end-to-end workflows

---

## Installation

### Prerequisites

- Node.js 18+ (recommended)
- npm, pnpm, or yarn
- Git
- Optional: Python 3.10+ for auxiliary tooling
- Optional: API keys for your selected model backends

### Install from npm (placeholder package)

- npm install -g super-pro

### Or use locally from source

- git clone https://github.com/adminsairolotech-bit/super-pro.git
- cd super-pro
- npm install

---

## Quick Start

1. Initialize configuration:
- super-pro init

2. Validate environment and integrations:
- super-pro doctor

3. Run first methodology cycle:
- super-pro run --flow spec-plan-execute-review --goal "Build a production-ready feature module"

4. Generate a project report:
- super-pro report --format markdown --out ./reports/first-run.md

---

## Detailed Usage

### 1) Run methodology-first project flow

Create a task from intent:

- super-pro task create --title "Customer onboarding revamp" --type feature --priority high

Generate specification:

- super-pro spec generate --task onboarding-revamp --context ./context/product.md

Build implementation plan:

- super-pro plan generate --task onboarding-revamp --constraints ./context/constraints.yaml

Execute with assigned agents:

- super-pro execute --task onboarding-revamp --agents architect,implementer,reviewer

Run review + quality gates:

- super-pro review --task onboarding-revamp --checks tests,security,docs,ux

### 2) Use modular skills with agent backends

List available skills:

- super-pro skills list

Inspect a skill:

- super-pro skills show design-system

Run a skill with specific backend:

- super-pro skills run design-system --agent buddy-ai --input ./briefs/deck-brief.md

Switch backend dynamically:

- super-pro agents use buddy-ai
- super-pro skills run research-synthesis --input ./research/raw-notes.md

### 3) Design-system and brand token synchronization

Extract colors from assets:

- super-pro brand extract-colors --input ./assets/logo.svg --out ./tmp/colors.json

Sync brand tokens to design system:

- super-pro brand sync-tokens --source ./tmp/colors.json --target ./design/tokens.json

Validate visual assets:

- super-pro brand validate-asset --input ./assets/hero-banner.png --rules ./config/brand-rules.yaml

Generate slide/UI layout guidance from data tables:

- super-pro design layout-suggest --dataset ./data/slide-layouts.csv --content ./briefs/presentation.md

### 4) Curated resource ingestion and validation

Add a new resource:

- super-pro resources add --url https://example.com/tool --category agents --tags workflow,automation

Run governance checks:

- super-pro resources validate --links --metadata --duplicates

Regenerate alternative indexes:

- super-pro resources build-index --views az,created,updated,releases

### 5) Second-brain knowledge workflows

Capture notes from execution:

- super-pro brain capture --task onboarding-revamp --source ./reports/execution.log

Create evergreen synthesis:

- super-pro brain distill --topic onboarding --out ./knowledge/evergreen/onboarding.md

Query internal knowledge:

- super-pro brain query --q "best rollout checklist for onboarding feature"

### 6) Prompt research, security, and red-team practices

Run prompt benchmark set:

- super-pro prompts benchmark --suite core-evals --agent claude

Scan for unsafe prompt patterns:

- super-pro security prompt-audit --input ./prompts --policy ./policies/prompt-safety.yaml

Generate findings summary:

- super-pro security report --type prompt-audit --out ./reports/prompt-audit.md

---

## Configuration

`super-pro` supports layered configuration (defaults -> repo config -> environment -> CLI overrides).

Typical config domains:

- `agents`
  - default provider
  - model mapping
  - temperature/token limits
- `skills`
  - enabled/disabled skills
  - skill-specific input schemas
- `flows`
  - workflow presets (spec-plan-execute-review)
  - quality gates
- `design`
  - token sources
  - validation rules
  - asset quality thresholds
- `resources`
  - submission policies
  - required metadata
  - indexing behavior
- `security`
  - prompt safety policies
  - red-team profiles
  - secrets scanning options
- `docs`
  - generated README variants
  - changelog/release metadata automation

Example environment variables:

- `SUPER_PRO_AGENT=claude`
- `SUPER_PRO_MODEL=claude-3-7-sonnet`
- `SUPER_PRO_CONFIG=./super-pro.config.yaml`
- `SUPER_PRO_LOG_LEVEL=info`

---

## CLI Reference

Core command groups:

- `super-pro init`
- `super-pro doctor`
- `super-pro run`
- `super-pro spec|plan|execute|review`
- `super-pro skills ...`
- `super-pro agents ...`
- `super-pro brand ...`
- `super-pro design ...`
- `super-pro resources ...`
- `super-pro brain ...`
- `super-pro prompts ...`
- `super-pro security ...`
- `super-pro report ...`

Use:

- `super-pro --help`
- `super-pro <command> --help`

---

## Quality, CI/CD, and Governance

`super-pro` includes policy-driven automation inspired by mature repository operations:

- Automated link and metadata validation
- Repository health checks and stale-state detection
- Submission enforcement for issues/PRs/resources
- Release metadata generation and publication helpers
- Pre-commit checks for docs and formatting consistency
- Contribution templates for predictable collaboration
- Optional bot-assisted moderation and triage workflows

This ensures the repository remains healthy as it scales in contributors, artifacts, and integrations.

---

## Contributing

Contributions are welcome across:

- Skills
- Agents/provider configs
- Hooks and commands
- Plugin adapters
- UI/UX data packs
- Knowledge workflows
- Security policies and benchmarks
- Documentation and examples

Please see `CONTRIBUTING.md` for:

- development setup
- branching/commit conventions
- test and validation requirements
- review criteria
- governance and code of conduct references

If you are submitting new resources or prompt datasets, follow the submission templates and validation checks to ensure high signal quality.

---

## License

This project is licensed under the terms of the license defined in `LICENSE`.

Recommended for this synthesized repository: a permissive OSS license (e.g., MIT) for maximal reuse, while preserving attribution in docs and acknowledgments.

---

## Acknowledgments

`super-pro` is built by synthesizing ideas and patterns from:

- `adminsairolotech-bit/awesome-claude-code`
- `adminsairolotech-bit/ui-ux-pro-max-skill`
- `adminsairolotech-bit/everything-claude-code`
- `adminsairolotech-bit/cloude-ai-agiant-superpowers`
- `adminsairolotech-bit/multi-ai-system_prompts_leaks`
- `adminsairolotech-bit/second-brain-skills`
- `adminsairolotech-bit/HowToHunt`

Special thanks to all maintainers and contributors of the source repositories for their work on automation, skill systems, methodology, design operations, prompt research, and knowledge practices that informed this unified project.
