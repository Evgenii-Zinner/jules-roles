# AGENTS.md — Operational Context for AI Agents

> This file is a high-density, token-efficient blueprint for autonomous coding agents (Jules, Cursor, Claude Code, Copilot). Keep this file strictly under 200 lines.

---

## 🚨 Critical Invariants (Never Violate)
1. **Zero-Anchor Mandate:** Never use hardcoded checklists, pattern lists, or keyword parentheticals in agent role definitions. Traversal must be driven by workspace filesystem inspection.
2. **Conventional Commits:** All PR titles and git commits MUST strictly adhere to Conventional Commits: `<type>(<scope>): <description>`.
3. **Atomic Scope:** PRs must be bounded by a single cohesive unit of work rather than arbitrary line truncation or rigid file-count handcuffs. Never cut tests, refactorings, or documentation midway through to fit artificial limits. Updating journal files in `.jules/` along with related code/test/fixture changes is expected; auto-generated lockfiles are excluded from line count limits.
4. **Behavioral Invariance:** Never alter runtime logic or breaking public contracts unless explicitly assigned to fix a verified bug.

---

## 🗺️ Codebase Topology & Domain Ownership

```
jules-roles/
├── README.md        # Public overview, role matrix, and architectural rationale
├── LICENSE          # MIT open-source license
├── AGENTS.md        # High-density agent operational rules (this file)
│
├── .github/
│   ├── CONTRIBUTING.md        # Contribution guidelines, Conventional Commits & tooling
│   ├── CODE_OF_CONDUCT.md     # Contributor Covenant v2.1 standards
│   ├── SECURITY.md            # Vulnerability reporting protocol (security@ezinner.com)
│   ├── FUNDING.yml            # Sponsorship configuration
│   └── PULL_REQUEST_TEMPLATE.md
│
├── scripts/
│   ├── jules_dispatch.py          # [tool] Jules REST API CLI session dispatcher
│   └── dispatch_parallel_tasks.py # [tool] Concurrent batch task dispatcher (disjoint)
│
├── roles/
│   ├── TEMPLATE.md      # Universal Zero-Anchor blueprint for creating new roles
│   ├── scribe.md        # [docs] Source Code Specifications (TSDoc/Google docstrings on full files)
│   ├── validator.md     # [test] QA & Full Test File Authoring (AAA, mocks & boundary validation)
│   ├── craftsman.md     # [refactor] Clean Code & Structural Refactoring (Cognitive complexity, guard clauses)
│   ├── prism.md         # [refactor] Type System Safety (Strict typing, discriminated unions)
│   ├── mason.md         # [refactor] Architecture & Modular Cohesion (Cohesive sub-domain extraction, DRY/YAGNI/KISS)
│   ├── tether.md        # [chore] Dependency Health & Package Hygiene (Minor/patch upgrades)
│   ├── sentinel.md      # [fix] Application Security & Trust Boundaries (Defensive hardening)
│   ├── vigil.md         # [fix] Observability, Error Resilience & Diagnostic Telemetry
│   ├── palette.md       # [style] UI Layout Resilience & Design Token Alignment
│   ├── beacon.md        # [fix] Accessibility (a11y) & Semantic UI Interactions
│   ├── polyglot.md      # [refactor] Internationalization (i18n) & Translation Catalog
│   ├── conduit.md       # [ci] CI/CD, Workflows & Pipeline Efficiency
│   ├── thrift.md        # [perf] Edge Resource, Caching & Data Access Efficiency
│   ├── herald.md        # [docs] Repository Presentation, Community Standards, READMEs & AI Context
│   └── cartographer.md  # [docs] Codebase Topology & AST RepoMap Skeletons
│
└── .jules/          # Persistent agent memory & Least-Recently-Visited rotation logs
```

---

## 🛠️ Validation & Tooling Conventions
- **Markdown Linting & Formatting:** Follow standard GitHub-flavored Markdown.
- **File Links:** Always format internal links with full relative or file URI paths.
- **Subagent Delegation:** When creating new roles, always adhere to `TEMPLATE.md`.

---

## 🧹 Memory Hygiene: Compacting `.jules/` Journals
Autonomous agents read their corresponding `.jules/<role>.md` journal on startup. To prevent token bloat over prolonged use:
- **Max History:** Journals should maintain only the **last 10 entries** for recency rotation.
- **Distillation Rule:** If a critical repository gotcha or architectural constraint is discovered, promote it directly into `AGENTS.md` or `README.md` and prune old entries from the journal.
