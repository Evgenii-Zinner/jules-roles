# AGENTS.md — Operational Context for AI Agents

> This file is a high-density, token-efficient blueprint for autonomous coding agents (Jules, Cursor, Claude Code, Copilot). Keep this file strictly under 200 lines.

---

## 🚨 Critical Invariants (Never Violate)
1. **Zero-Anchor Mandate:** Never use hardcoded checklists, pattern lists, or keyword parentheticals in agent role definitions. Traversal must be driven by workspace filesystem inspection.
2. **Conventional Commits:** All PR titles and git commits MUST strictly adhere to Conventional Commits: `<type>(<scope>): <description>`.
3. **Atomic Scope:** PRs must be strictly bounded to `< 50 lines of diff` (or `< 120 lines` for pure code relocation by Mason; auto-generated lockfiles for Tether are excluded from line count limits).
4. **Behavioral Invariance:** Never alter runtime logic or breaking public contracts unless explicitly assigned to fix a verified bug.

---

## 🗺️ Codebase Topology & Domain Ownership

```
jules-roles/
├── README.md        # Public overview, role matrix, and architectural rationale
├── CONTRIBUTING.md  # Contribution guidelines & Conventional Commits protocol
├── LICENSE          # MIT open-source license
├── TEMPLATE.md      # Universal Zero-Anchor blueprint for creating new roles
├── AGENTS.md        # High-density agent operational rules (this file)
│
├── scribe.md        # [docs] Documentation & Specifications (TSDoc/Google docstrings)
├── validator.md     # [test] QA & Assertion Depth (AAA, boundary validation)
├── craftsman.md     # [refactor] Clean Code (Cognitive complexity, guard clauses)
├── prism.md         # [refactor] Type System Safety (Strict typing, discriminated unions)
├── mason.md         # [refactor] Architecture & Modular Cohesion (DRY/YAGNI/KISS)
├── tether.md        # [chore] Dependency Health & Package Hygiene (Minor/patch upgrades)
├── sentinel.md      # [fix] Application Security & Trust Boundaries (Defensive hardening)
├── vigil.md         # [fix] Observability, Error Resilience & Diagnostic Telemetry
├── palette.md       # [style] UI Layout Resilience & Design Token Alignment
├── beacon.md        # [fix] Accessibility (a11y) & Semantic UI Interactions
├── polyglot.md      # [refactor] Internationalization (i18n) & Translation Catalog
├── conduit.md       # [ci] CI/CD, Workflows & Pipeline Efficiency
├── thrift.md        # [perf] Edge Resource, Caching & Data Access Efficiency
├── herald.md        # [docs] Repository Presentation, Community Standards & AI Context
├── cartographer.md  # [docs] Codebase Topology & AST RepoMap Skeletons
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
