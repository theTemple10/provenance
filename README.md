# Provenance

**"Know what a codebase is worth before you trust it — or buy it."**

micro1 Agentic Workflows Hackathon — Aug 28–30, 2026

---

## The Problem

Anyone who has to trust a codebase they didn't write faces the same bottleneck: a README and a working demo tell you almost nothing about real quality. You have to actually run the build/tests, read the architecture, check git history for red flags, and weigh technical debt — and two reviewers looking at the same repo can walk away with different verdicts.

**The gap between visible quality and actual quality is usually hiding in what nobody looked at** — branches, tests that don't run, dependencies nobody updated.

## The Solution

Provenance is an engineering reviewer agent that goes beyond README-level inspection. It:

1. **Inspects git history** — catches unmerged branches with substantial work
2. **Runs the actual test suite** — verifies tests pass, not just exist
3. **Analyzes dependencies** — flags stale or unpinned deps
4. **Produces evidence-backed scores** — every claim points to a source

## Agent Disclosure

- **Agent**: OpenCode running MiMo 2.5 (free/local model)
- **Builder**: Victor Oluwatimileyin Akinremi
- **Tech stack**: Python 3 stdlib only for tooling, git CLI via subprocess

## The Trap Case

The strongest eval repo is a synthetic "hidden branch" case:

- **main branch**: Basic Flask REST API with CRUD (150 LOC, tests pass)
- **unmerged branch `feature/auth-system`**: Full JWT auth system (400+ LOC more, never merged)

A README-only review scores this 4-5/10. The agent, which checks `git branch -a`, should catch the hidden work and score it 7-8/10 — matching the ground truth.

## Eval Set

| # | Repo | Why it's in the set |
|---|------|----------------------|
| 1 | APIGuardian | Known-good, sanity-check against ground truth |
| 2 | Weaker repo | Known-mediocre, tests thin or missing |
| 3 | Trap case (synthetic) | The hard case — mirrors the Conclave discovery |
| 4 | taverntesting/tavern | Well-maintained, good tests, CI |
| 5 | jgontrum/spacy-api-docker | Mediocre quality, Docker-dependent |
| 6 | sameerkumar18/aztro | Risky, less maintained, no tests |

**Note**: 6 repos, not 10 — honest scope beats padding given the timeline.

## Results

| Metric | Baseline | Agent (Provenance) | Ground Truth | Change |
|--------|----------|-------------------|--------------|--------|
| Rank correlation | — | — | — | — |
| Caught hidden-branch case? | No | — | Yes | — |
| Time per repo | — | — | — | — |
| Cost per repo | — | — | — | — |

## Project Structure

```
provenance/
  README.md                  <- this file
  CHANGELOG.md                <- improvement changelog
  baseline/
    baseline_review.py        <- dumb version: README + file tree only
  agent/
    system_prompt.md          <- agent instructions
    run_agent.py              <- wires OpenCode/MiMo to tools
  eval/
    rubric.md                 <- scoring rubric
    repos.md                  <- 6 eval repos + ground truth scores
    results.md                <- final results table
  trajectories/
    <repo>_baseline.log       <- raw baseline session logs
    <repo>_agent.log          <- raw agent session logs
  docs/
    reproduction.md           <- exact commands, versions, runtime
  video/
    script.md                 <- video script
```

## License

MIT
