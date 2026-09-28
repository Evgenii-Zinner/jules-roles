# Jules Roles Base 🤖

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg)](https://conventionalcommits.org)
[![Architecture: Zero-Anchor](https://img.shields.io/badge/Architecture-Zero--Anchor-green.svg)](#-the-solution-zero-anchor-structural-traversal)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

A curated library of persona configurations for **Jules** (Google's asynchronous AI coding agent). Each role specializes in a discrete software development discipline, systematically traversing the entire codebase over time to execute atomic, high-impact improvements using strict **Conventional Commits**.

---

## 📚 Active Roles

| Role | Emoji | Focus Area | Primary Objective | Journal Path | Traversal Strategy | Standard |
| :--- | :---: | :--- | :--- | :--- | :--- | :--- |
| [Scribe](scribe.md) | 📝 | Conventional Docs & Specs | Eliminates information asymmetry across codebase subsystems | `.jules/scribe.md` | Filesystem LRU Directory Traversal | Conventional Commits + TSDoc/Google Docstrings |
| [Validator](validator.md) | 🧪 | QA & Test Assertion Integrity | Eliminates coverage theater and verifies unasserted boundaries | `.jules/validator.md` | Filesystem LRU Directory Traversal | Conventional Commits (`test(<scope>): ...`) + AAA |
| [Craftsman](craftsman.md) | 🛠️ | Clean Code & Structural Refactoring | Reduces cyclomatic complexity, dead code, and cognitive friction | `.jules/craftsman.md` | Filesystem LRU Directory Traversal | Conventional Commits (`refactor(<scope>): ...`) |
| [Prism](prism.md) | 💎 | Type Safety & Contract Integrity | Eliminates `any`, type escapes, and loose interface definitions | `.jules/prism.md` | Filesystem LRU Directory Traversal | Conventional Commits (`refactor(<scope>): ...`) |
| [Tether](tether.md) | 🧹 | Dependency Health & Package Hygiene | Upgrades safe minor/patch dependencies and prunes orphaned packages | `.jules/tether.md` | Manifest & Lockfile Outdated Inspection | Conventional Commits (`chore(deps): ...`) |
| [Sentinel](sentinel.md) | 🛡️ | Application Security & Hardening | Audits trust boundaries, prevents data leaks, and fixes vulnerabilities | `.jules/sentinel.md` | Filesystem LRU Directory Traversal | Conventional Commits (`fix(<scope>): ...`) |
| [Palette](palette.md) | 🎨 | UI Resilience & Visual Consistency | Solves layout brittleness, viewport breakdown, and design token drift | `.jules/palette.md` | Filesystem LRU Directory Traversal | Conventional Commits (`style(<scope>): ...`) |
| [Mason](mason.md) | 🧱 | Architecture & Modular Cohesion | Balances DRY/YAGNI/KISS, decomposes God files without micro-file sprawl | `.jules/mason.md` | Filesystem LRU Directory Traversal | Conventional Commits (`refactor(<scope>): ...`) |
| [Herald](herald.md) | 🎺 | Repository Presentation & AI Context | GitHub community standards (README, Contributing, Sponsors) & lean AGENTS.md | `.jules/herald.md` | Root & .github/ Inspection | Conventional Commits (`docs(repo): ...`) |
| [Cartographer](cartographer.md) | 🗺️ | Codebase Topology & AST RepoMap | Generates high-density, signature-only outlines (90% token reduction) | `.jules/cartographer.md` | Filesystem LRU Directory Traversal | Conventional Commits (`docs(map): ...`) |

---

## 🔬 The Anchor Problem: Why Examples & Checklists Fail

In autonomous agents, **any concrete list or parenthetical example acts as an anchor trap**:

```markdown
# ❌ The Anchor Trap (Even subtle parentheticals cause failure!)
"Inspect high-traffic surfaces (CLI flags, root router, public exports, config schemas)"
```

### What happens in prolonged use?
1. **Keyword Fixation:** The LLM's attention mechanism locks onto the explicit words (`CLI`, `router`, `exports`, `schemas`). It filters its search space solely to files matching those keywords, completely ignoring the other 90% of the repository.
2. **Exhaustion & Hallucination:** Once it has checked those specific surfaces, it either repeats edits on them or hallucinates trivial changes because it was never taught how to explore the rest of the codebase.
3. **Loss of Autonomy:** The agent behaves like a rigid regex script rather than an autonomous engineer.

---

## 🧭 The Solution: Zero-Anchor Structural Traversal

Modern agentic engineering eliminates lists of targets entirely. Instead, the agent is guided by **mechanical filesystem traversal** combined with **domain-specific first-principles evaluation**:

```
┌────────────────────────────────────────────────────────────────────────┐
│ 1. Structural Filesystem Discovery                                     │
│    Reads repository directory tree directly from the workspace.        │
├────────────────────────────────────────────────────────────────────────┤
│ 2. Least-Recently-Visited (LRU) Directory Selection                    │
│    Reads .jules/<role>.md to find the least recently audited directory.│
├────────────────────────────────────────────────────────────────────────┤
│ 3. Axiomatic Evaluation (Zero-Anchor Questions)                        │
│    Evaluates code using first-principles questions (e.g. Asymmetry).   │
├────────────────────────────────────────────────────────────────────────┤
│ 4. Atomic Execution (< 50 LOC) & Deterministic Verification           │
├────────────────────────────────────────────────────────────────────────┤
│ 5. Conventional Commits: <type>(<audited-directory>): <description>   │
└────────────────────────────────────────────────────────────────────────┘
```

### 1. Filesystem-Driven Navigation (LRU Traversal)
- The prompt mentions **no file names, directory names, or keywords**.
- The agent runs directory listing commands at runtime to discover the project's actual source folders.
- It consults `.jules/<role>.md` to identify which folder was audited least recently (or never).
- **Result:** Over 10, 20, or 50 runs, the agent systematically audits the *entire* codebase, rotating through every subsystem without human intervention.

### 2. Axiomatic Evaluative Questions (No Keyword Anchors)
Instead of looking for specific syntax patterns, the agent asks first-principles questions about the code it encounters:
- **For Scribe 📝 (Information Asymmetry):**
  > *"Where does this implementation enforce constraints, handle error conditions, or produce side effects that are invisible or ambiguous to someone reading only the interface declaration?"*
- **For Craftsman 🛠️ (Cognitive Simplicity):**
  > *"Where does this code exhibit structural convolution or unnecessary cognitive friction that can be simplified into clean, declarative code without altering external behavior?"*
- **For Sentinel 🛡️ (Unverified Trust):**
  > *"Where does this code consume external, persistent, or unvalidated state without asserting boundaries?"*

### 3. Conventional Commits with Directory Scoping
The PR title format enforces clean, machine-readable history where `<scope>` reflects the physical subsystem audited:
```text
docs(services): document timeout constraints and error variants
refactor(database): flatten nested branching using guard clauses
fix(middleware): assert header length boundaries before buffer allocation
```

---

## 🛠️ How to Create a New Role

Use [`TEMPLATE.md`](TEMPLATE.md) as the starting blueprint:

1. **Copy the template:**
   ```bash
   cp TEMPLATE.md roles/my-role.md
   ```
2. **Define Persona & Moniker:** Choose an evocative noun name and emoji.
3. **Define the Core Evaluative Question:** Craft a single, rigorous first-principles question for your domain. **Do not include parenthetical lists of file types or patterns.**
4. **Set Up the Journal Path:** Point the journal to `.jules/<role-slug>.md` with the LRU traversal rule enabled.
