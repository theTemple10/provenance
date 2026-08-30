# Results Table

Final baseline vs agent vs ground truth comparison.

## Overall Results

| Metric | Baseline | Agent (Provenance) | Ground Truth | Change |
|--------|----------|-------------------|--------------|--------|
| Rank correlation to my ranking | — | — | — | — |
| Caught the hidden-branch case? | No (can't see it) | — | Yes | — |
| Time per repo | — | — | — | — |
| Cost per repo (API/compute) | — | — | — | — |

## Per-Repo Scores

| Repo | Baseline Score | Agent Score | Ground Truth | Notes |
|------|---------------|-------------|--------------|-------|
| APIGuardian | — | — | 7 | Placeholder |
| Weaker repo | — | — | 4 | Placeholder |
| Trap case | — | — | 8 | Must catch hidden branch |
| tavern | — | — | 8 | Well-maintained |
| spacy-api-docker | — | — | 5 | Mediocre |
| aztro | — | — | 3 | Risky |

## Trap Case Deep Dive

**The hard case — explained in depth:**

The trap case is a synthetic Flask REST API where:
- **main branch**: Basic CRUD (4 routes, 150 LOC, 15 passing tests)
- **unmerged branch `feature/auth-system`**: Full JWT auth (user models, middleware, 6+ routes, 400+ LOC more, 20+ tests)

**Ground truth**: This repo is actually 8/10 quality — the auth system is substantial, well-tested, and production-ready.

**Baseline result**: Scores it 4-5/10. Can't see the auth branch because it only reads README + file tree.

**Agent result**: Should score it 7-8/10. Catches the hidden branch via `git branch -a`, runs tests on both branches, flags the unmerged work.

**Why this matters**: This mirrors the Conclave discovery — a teammate's substantial work sat on an unmerged branch, invisible to anyone who just cloned main. A README-only review would have scored that repo as thinner than it actually was.

## Trajectory Logs

Raw session transcripts for each repo run:
- `trajectories/<repo>_baseline.log` — baseline session
- `trajectories/<repo>_agent.log` — agent session
