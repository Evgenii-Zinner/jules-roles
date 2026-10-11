# Contributing to Jules Roles Base

Thank you for your interest in contributing! This repository provides a curated collection of standalone, Zero-Anchor autonomous agent personas, along with developer tooling to interact programmatically with Google Jules.

---

## 🎯 Guiding Principles

When proposing changes, new agent roles, or tooling updates, adhere strictly to our core invariants:

1. **Zero-Anchor Mandate:** Never use hardcoded pattern lists, keyword parentheticals, or static checklists in role prompts. Traversal must be driven by workspace filesystem inspection and first-principles axiomatic questions.
2. **Conventional Commits:** All PR titles and git commits must strictly follow `<type>(<scope>): <description>` (e.g. `feat(roles): add new role`, `fix(scripts): handle 429 rate limit`).
3. **Atomic Scope:** PRs should be bounded by a single cohesive unit of work (such as authoring a complete test suite with mocks, refactoring complex logic, sub-domain relocation, or full-file specifications) without arbitrary line truncation or contradictory file-count boundaries.
4. **Standalone & Portable:** Each role markdown file must be 100% self-contained without hardcoded coupling or references to other roles.
5. **Zero Sensitive Information:** Never commit API keys, personal secrets, auth tokens, or private personal emails. Use environment variables or gitignored credential files.

---

## 🛠️ Adding a New Role

To create a new role:
1. Copy [`roles/TEMPLATE.md`](../roles/TEMPLATE.md) to your new role file:
   ```bash
   cp roles/TEMPLATE.md roles/your-role.md
   ```
2. Define a clear persona with a concise moniker and emoji.
3. Formulate a single first-principles **Core Evaluative Question** with zero bulleted smell categories or parenthetical keywords.
4. Define the journal path in `.jules/<your-role>.md` using Least-Recently-Visited (LRU) directory selection.
5. Update [`README.md`](../README.md) and [`AGENTS.md`](../AGENTS.md) to include the new role.

---

## 🐍 Working with Python Dispatcher Scripts

This repository includes helper scripts in `scripts/` to interact programmatically with the **Google Jules REST API (v1alpha)**:

### 1. `scripts/jules_dispatch.py` (CLI Session Manager)
Provides command-line control over Jules sessions:
- **List sessions:** `python3 scripts/jules_dispatch.py list`
- **Inspect session:** `python3 scripts/jules_dispatch.py get <session_id>`
- **Create session:** `python3 scripts/jules_dispatch.py create --prompt "Execute roles/craftsman.md against auth module" --title "Refactor Auth"`
- **View activity stream:** `python3 scripts/jules_dispatch.py activities <session_id>`
- **Send follow-up message:** `python3 scripts/jules_dispatch.py message <session_id> --message "Please add unit tests"`
- **Approve proposed plan:** `python3 scripts/jules_dispatch.py approve <session_id>`
- **Delete session:** `python3 scripts/jules_dispatch.py delete <session_id>`

### 2. `scripts/jules_dispatch_many.py` (Parallel Batch Dispatcher)
Dispatches batches of disjoint tasks to Jules concurrently:
- Verifies zero file intersection across concurrent tasks to avoid merge conflicts.
- Supports dry-run validation: `python3 scripts/jules_dispatch_many.py --tasks scripts/tasks.example.json --dry-run`
- Dispatches specific task IDs: `python3 scripts/jules_dispatch_many.py --tasks tasks.json --task 1`
- Automatically updates a local session registry (`.jules/active_sessions.json`).

### 🔒 Script Security & Contribution Rules
- **Authentication:** Authenticate using the `JULES_API_KEY` environment variable. A local `.jules_key` file in the repository root or parent directory is also supported and is strictly `.gitignore`d.
- **Zero Secrets Policy:** Never commit hardcoded API keys, auth tokens, or credentials to any script or fixture.
- **Dependency Philosophy:** Scripts should prioritize Python 3 standard library (`urllib.request`, `json`, `argparse`) so they remain lightweight and runnable without requiring heavy virtual environments.
- **Error Handling:** Gracefully handle HTTP errors, rate limits, and network anomalies with actionable terminal messages.

---

## 📜 Pull Request Process

1. Fork the repository and create your branch from `main`.
2. Format all markdown cleanly adhering to GitHub-flavored Markdown.
3. Verify that any Python modifications adhere to PEP 8, contain zero secrets, and run cleanly without syntax errors.
4. Submit your pull request with a descriptive Conventional Commit title.
