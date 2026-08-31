# Results Table

Final baseline vs agent vs ground truth comparison.

## Overall Results

| Metric | Baseline | Agent (Provenance) | Ground Truth | Change |
|--------|----------|-------------------|--------------|--------|
| Rank correlation to my ranking | — | — | — | — |
| Caught the hidden-branch case? | No (score: 4) | Yes (score: 6) | Yes (score: 8) | Agent found hidden branch |
| Time per repo | <5s | 30-60s | — | — |
| Cost per repo (API/compute) | ~$0.001 | ~$0.01 | — | Groq free tier |

## Per-Repo Scores

| Repo | Baseline Score | Agent Score | Ground Truth | Notes |
|------|---------------|-------------|--------------|-------|
| APIGuardian | — | — | 7 | Placeholder |
| Weaker repo | — | — | 4 | Placeholder |
| Trap case | 4 | 6 | 8 | Agent caught hidden branch |
| tavern | — | — | 8 | Well-maintained |
| spacy-api-docker | — | — | 5 | Mediocre |
| aztro | — | — | 3 | Risky |

## Trap Case Deep Dive

**The hard case — explained in depth:**

The trap case is a synthetic Flask REST API where:
- **main branch**: Basic CRUD (4 routes, 150 LOC, 15 passing tests)
- **unmerged branch `feature/auth-system`**: Full JWT auth (user models, middleware, 6+ routes, 400+ LOC more, 20+ tests)

**Ground truth**: This repo is actually 8/10 quality — the auth system is substantial, well-tested, and production-ready.

**Baseline result**: Scores it 4/10. Can't see the auth branch because it only reads README + file tree.

**Agent result**: Scores it 6/10. Catches the hidden branch via `git branch -a`, runs tests (12 pass), flags the unmerged work. The agent correctly identified the hidden branch but the LLM gave a conservative score.

**Why this matters**: This mirrors the Conclave discovery — a teammate's substantial work sat on an unmerged branch, invisible to anyone who just cloned main. A README-only review would have scored that repo as thinner than it actually was.

## Trajectory Logs

Raw session transcripts for each repo run:
- `trajectories/<repo>_baseline.log` — baseline session
- `trajectories/<repo>_agent.log` — agent session
