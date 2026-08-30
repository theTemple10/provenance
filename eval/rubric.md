# Provenance Scoring Rubric

This rubric is used to evaluate codebases across 4 dimensions. Each dimension is scored 1-10.

---

## Dimension 1: Architecture Clarity (1-10)

| Score | Criteria |
|-------|----------|
| 1-2 | No clear structure, files dumped randomly, no entry points |
| 3-4 | Some organization but messy, unclear module boundaries |
| 5-6 | Acceptable structure, entry points exist, some separation of concerns |
| 7-8 | Clean architecture, clear module boundaries, well-defined entry points |
| 9-10 | Excellent architecture, follows conventions, easy to navigate and extend |

**What to check:**
- File/directory organization
- Entry points (main files, CLI, web routes)
- Module boundaries and imports
- Separation of concerns
- Naming conventions

---

## Dimension 2: Test Health (1-10)

| Score | Criteria |
|-------|----------|
| 1-2 | No tests at all, or tests that don't run |
| 3-4 | Some tests exist but are minimal, don't cover core logic |
| 5-6 | Reasonable test coverage, most core logic tested |
| 7-8 | Good coverage, tests pass, cover edge cases |
| 9-10 | Excellent coverage, tests are meaningful, CI integration |

**What to check:**
- Do tests exist?
- Do they actually run and pass?
- Do they cover real logic (not just "hello world")?
- Is there CI configuration?
- What's the rough coverage?

---

## Dimension 3: Hidden Risk (1-10)

**Lower score = more hidden risk found**

| Score | Criteria |
|-------|----------|
| 1-2 | Major hidden risk: unmerged branches with substantial work, critical security issues |
| 3-4 | Significant hidden risk: stale deps, no CI, undisclosed work |
| 5-6 | Moderate hidden risk: some stale deps, minor issues |
| 7-8 | Low hidden risk: minor issues only |
| 9-10 | Minimal hidden risk: clean, well-maintained |

**What to check:**
- `git branch -a` — unmerged branches with substantial commits?
- `git log --all` vs `git log main` — work outside main?
- Dependency health (outdated, unpinned)
- CI/CD configuration
- TODO/FIXME density
- Security concerns

---

## Dimension 4: Overall Trust (1-10)

| Score | Criteria |
|-------|----------|
| 1-2 | Do not trust or acquire as-is |
| 3-4 | Significant work needed before trusting |
| 5-6 | Acceptable with some caveats |
| 7-8 | Trustworthy, would acquire with minor reservations |
| 9-10 | Highly trustworthy, production-ready |

**What to check:**
- Would you acquire this repo?
- Would you inherit this codebase?
- Would you trust this for production?
- Overall impression after reviewing all dimensions

---

## Scoring Guidelines

1. **Be honest** — don't inflate scores to make the agent look good
2. **Be consistent** — use the same standards across all repos
3. **Evidence-based** — tie scores to specific observations
4. **Trap case special rule** — if the agent misses the hidden branch, its hidden_risk score should be penalized heavily (the whole point is catching invisible work)

---

## Expected Agent vs Baseline Performance

| Scenario | Baseline | Agent |
|----------|----------|-------|
| Trap case (hidden branch) | Should score 4-5 (can't see auth branch) | Should score 7-8 (catches hidden branch) |
| Well-maintained repo | Should score 7-8 | Should score 8-9 |
| Risky repo | Should score 3-4 | Should score 2-3 (catches more risk) |

The agent's advantage should be most visible on the trap case — that's the core contribution.
