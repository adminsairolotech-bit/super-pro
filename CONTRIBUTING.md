# Contributing to super-pro

Thanks for your interest in contributing to **super-pro**!  
This project benefits from clear, focused, and well-tested contributions.

## Quick Start

### 1) Fork the repository
- Go to the project page on GitHub.
- Click **Fork** (top-right) to create your copy under your account.

### 2) Clone your fork
- Clone your fork locally:
  - `git clone https://github.com/<your-username>/super-pro.git`
- Enter the project:
  - `cd super-pro`
- Add upstream remote:
  - `git remote add upstream https://github.com/<org-or-owner>/super-pro.git`

### 3) Set up development environment
- Use Python 3.11+ (recommended).
- Create and activate a virtual environment:
  - `python -m venv .venv`
  - `source .venv/bin/activate` (macOS/Linux) or `.venv\Scripts\activate` (Windows)
- Install dependencies:
  - `pip install -U pip`
  - `pip install -e .[dev]`
- If `.[dev]` is unavailable, install from project files (for example `requirements.txt` and `requirements-dev.txt`).

## Running Tests

- Run full test suite:
  - `pytest`
- Run with coverage (if configured):
  - `pytest --cov=super_pro --cov-report=term-missing`
- Run linters/formatters before opening a PR:
  - `ruff check .`
  - `black .`
  - `isort .`
  - `mypy super_pro` (if type checking is enabled)

## Workflow for Contributions

1. Sync with upstream:
   - `git fetch upstream`
   - `git checkout main`
   - `git merge upstream/main`
2. Create a feature branch:
   - `git checkout -b feat/<short-description>`
3. Make focused commits with clear messages.
4. Run tests and quality checks locally.
5. Push branch to your fork:
   - `git push origin feat/<short-description>`
6. Open a Pull Request to `main`.

## Pull Request Guidelines

- Keep PRs small and single-purpose.
- Include:
  - What changed
  - Why it changed
  - How it was tested
- Link related issues (e.g., `Closes #123`).
- Add/update tests for behavior changes.
- Update docs when relevant.
- Ensure CI passes before requesting review.

## Code Style Guidelines

- Follow **PEP 8**.
- Use type hints for new/updated Python code.
- Prefer small, composable functions.
- Write descriptive names; avoid abbreviations.
- Add docstrings for public modules, classes, and functions.
- Keep imports ordered and unused code removed.
- Use project tooling defaults (Black/Ruff/isort) instead of manual formatting tweaks.

## Commit Message Suggestions

Use clear, conventional prefixes where possible:
- `feat:` new feature
- `fix:` bug fix
- `docs:` documentation
- `refactor:` internal code change
- `test:` tests added/updated
- `chore:` tooling/maintenance

Example: `feat: add prompt routing for multi-source synthesis`

## Reporting Issues

When opening an issue, include:
- Environment (OS, Python version)
- Steps to reproduce
- Expected vs actual behavior
- Logs/screenshots if helpful

## Community Expectations

Be respectful, constructive, and collaborative.  
By contributing, you agree to follow the project’s Code of Conduct (if present).