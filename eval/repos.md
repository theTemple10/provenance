# Eval Repos — Ground Truth Scores

Scored by the reviewer (Victor) BEFORE running the agent, to avoid anchoring bias.

## Rubric Dimensions

| Dimension | What it measures |
|-----------|-----------------|
| Architecture clarity (1-10) | Module boundaries, entry points, code organization |
| Test health (1-10) | Tests exist, pass, cover real logic |
| Hidden risk (1-10) | Lower = more hidden risk found (unmerged branches, stale deps, no CI) |
| Overall (1-10) | Would you trust/acquire this as-is? |

---

## Repo 1: APIGuardian (Placeholder — Victor's own repo)

- **URL**: https://github.com/theTemple10/APIGuardian (placeholder)
- **Why included**: Known-good, sanity-check against ground truth
- **Stack**: Python
- **LOC**: ~500

| Dimension | Score | Notes |
|-----------|-------|-------|
| Architecture | 7 | Clean structure, clear entry points |
| Test health | 8 | Tests exist, cover core logic |
| Hidden risk | 7 | No major hidden branches or stale deps |
| Overall | 7 | Solid, trustworthy project |

---

## Repo 2: Earlier/weaker repo (Placeholder — Victor's older work)

- **URL**: https://github.com/theTemple10/old-project (placeholder)
- **Why included**: Known-mediocre, tests thin or missing
- **Stack**: Python
- **LOC**: ~300

| Dimension | Score | Notes |
|-----------|-------|-------|
| Architecture | 5 | Some structure, but messy |
| Test health | 3 | Minimal tests, not covering edge cases |
| Hidden risk | 4 | Some stale deps, no CI |
| Overall | 4 | Needs work before trusting |

---

## Repo 3: Trap Case (Synthetic — built for this eval)

- **URL**: trap_repo/ (local, in this repo)
- **Why included**: The hard case — mirrors the Conclave discovery
- **Stack**: Flask REST API (Python)
- **LOC**: main=150, feature/auth=550+

| Dimension | Score | Notes |
|-----------|-------|-------|
| Architecture | 7 | Clean Flask app, well-organized modules |
| Test health | 8 | 15+ tests on main, 20+ on auth branch |
| Hidden risk | 3 | **CRITICAL**: 400+ LOC of JWT auth on unmerged branch — invisible to main-only review |
| Overall | 8 | Actually much better than main suggests |

**Key insight for this repo**: A README-only or demo-only review would score this 4-5/10. The agent must run `git branch -a` to catch the hidden auth system and score it 7-8/10.

---

## Repo 4: taverntesting/tavern (Well-maintained)

- **URL**: https://github.com/taverntesting/tavern
- **Why included**: Good quality baseline — tests, CI, active maintenance
- **Stack**: Python (pytest plugin)
- **LOC**: ~3000 (but well-structured)

| Dimension | Score | Notes |
|-----------|-------|-------|
| Architecture | 8 | Clean plugin architecture, pytest integration |
| Test health | 9 | Comprehensive test suite, CI |
| Hidden risk | 8 | Active, well-maintained, no hidden risk |
| Overall | 8 | High quality, production-ready |

---

## Repo 5: jgontrum/spacy-api-docker (Mediocre)

- **URL**: https://github.com/jgontrum/spacy-api-docker
- **Why included**: Mediocre quality — works but has issues
- **Stack**: Python (Flask + spaCy)
- **LOC**: ~800

| Dimension | Score | Notes |
|-----------|-------|-------|
| Architecture | 6 | Simple structure, but tightly coupled |
| Test health | 4 | Minimal tests, Docker-dependent |
| Hidden risk | 5 | Some stale deps, Docker complexity |
| Overall | 5 | Functional but needs polish |

---

## Repo 6: sameerkumar18/aztro (Risky)

- **URL**: https://github.com/sameerkumar18/aztro
- **Why included**: Risky — less maintained, potential issues
- **Stack**: Python (Flask)
- **LOC**: ~400

| Dimension | Score | Notes |
|-----------|-------|-------|
| Architecture | 5 | Simple but unclear structure |
| Test health | 2 | No visible tests |
| Hidden risk | 3 | Stale deps, no CI, unmaintained |
| Overall | 3 | Low trust, would not acquire as-is |

---

## Summary Table (to fill after running agent)

| Repo | Your Score | Baseline Score | Agent Score | Notes |
|------|-----------|---------------|-------------|-------|
| APIGuardian | 7 | — | — | Placeholder |
| Weaker repo | 4 | — | — | Placeholder |
| Trap case | 8 | 4 | 6 | Agent caught hidden branch |
| tavern | 8 | — | — | Well-maintained |
| spacy-api-docker | 5 | — | — | Mediocre |
| aztro | 3 | — | — | Risky |
