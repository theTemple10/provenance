# Improvement Changelog

Running lab notebook — every meaningful change, what was tried, why, what happened.

| Stage | What I tried & why | Evidence | Decision |
|-------|-------------------|----------|----------|
| Baseline | README + file listing only, single prompt | Trap repo scored 4/10, missed hidden branch entirely | Starting point established |
| Iteration 1 | Added `git branch -a` + `git log --all` inspection — baseline can't see undisclosed work | Trap repo score moved to 8/10, correctly flagged the unmerged auth system | Kept — this is the core differentiator |
| Iteration 2 | Added actual test execution instead of trusting README claims | Caught trap repo's auth branch has 20+ passing tests, main has 15+ | Kept — test health is a real signal |
| Iteration 3 | Tried adding dependency-vulnerability scanner | Added noise, low signal for repos this small, ate most of the time budget | Removed — not worth the complexity for this scope |
| Final | Combined git-history check + real test run + evidence-tagged scoring | Rank correlation to my own scoring: TBD vs baseline's TBD | Main contribution: git-history signal |

## Key Learnings

1. **Git history is the biggest signal** — checking branches and commit logs catches work that no README would mention
2. **Test execution matters** — many repos claim "fully tested" but fail to run tests
3. **Dependency scanning is overkill for small repos** — too much noise, not enough signal
4. **Evidence-backed scores are essential** — every claim must point to a source, or it's just an opinion

## What Was Cut

- **Dependency vulnerability scanner**: Added noise, low signal for repos under 2k LOC
- **CI config detection**: Nice-to-have but not critical for the core thesis
- **Code complexity metrics**: Would need AST parsing, not worth the time budget
