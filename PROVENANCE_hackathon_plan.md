# Provenance
**"Know what a codebase is worth before you trust it — or buy it."**

micro1 Agentic Workflows Hackathon — Aug 30–31, 2026
Agent: Groq free tier (Qwen 3.8-27B)
Builder: Victor Oluwatimileyin Akinremi

---

## 1. The story you're telling (Problem & User Value — 15 pts)

**Who has this problem?** Anyone who has to trust a codebase they didn't write and can't fully read in the time they have — an acquirer valuing a repo before paying for it, a technical lead inheriting a project, a fellowship reviewer judging a submission.

**The bottleneck:** A README and a working demo tell you almost nothing about real quality. You have to actually run the build/tests, read the architecture, check git history for red flags, and weigh technical debt — and two reviewers looking at the same repo can walk away with different verdicts.

**Your personal angle (use this — it's real and it's yours):** On Conclave, you audited a teammate's repo and found a large amount of real, working code sitting on an unmerged branch — completely invisible to anyone who just cloned `main`. A README-only or demo-only review would have scored that repo as thinner than it actually was. That's your whole thesis: **visible quality and actual quality diverge, and the gap is usually hiding in what nobody looked at** — branches, tests that don't run, dependencies nobody updated.

---

## 2. Repo structure (ONE repo, not two)

```
provenance/
  README.md                  <- intro, user, bottleneck, why it matters
  CHANGELOG.md                <- the improvement changelog table
  baseline/
    baseline_review.py        <- dumb version: README + file tree only, one prompt
  agent/
    system_prompt.md          <- the real agent's instructions (Section 4 below)
    run_agent.py               <- wires OpenCode/MiMo to the tools
  eval/
    rubric.md                  <- your scoring rubric (Section 6)
    repos.md                   <- the 6 eval repos + your ground-truth scores
    results.md                 <- final baseline vs agent vs your-score table
  trajectories/
    <repo-name>_baseline.log
    <repo-name>_agent.log      <- raw OpenCode session transcripts, one per repo
  docs/
    reproduction.md            <- exact commands, versions, runtime, cost
  video/
    script.md                  <- Section 8 below
```

---

## 3. Baseline design — deliberately dumb, but fair

The baseline gets **the exact same task and same repos**, but no tools, no execution, no git history.

**Baseline prompt (single LLM call, no agent, no code execution):**

```
You are reviewing a code repository to assess its quality for someone
considering acquiring or trusting it.

You are given ONLY:
- The README contents
- A top-level file/folder listing

You do NOT have access to run tests, read git history, or inspect
individual files beyond what's shown.

Based only on this, output a JSON object:
{
  "overall_score": 1-10,
  "architecture_note": "...",
  "risk_note": "...",
  "confidence": "low" (always say low — you have limited evidence)
}
```

This is your "one direct prompt with basic instructions" baseline per the brief — legitimate, not a strawman, just genuinely limited.

---

## 4. The agent — system prompt for OpenCode + MiMo 2.5

Paste this as `agent/system_prompt.md` and load it as the agent's system prompt in OpenCode.

```
ROLE
You are Provenance, an engineering reviewer agent. Given a local path to a
cloned git repository, produce a structured, evidence-backed quality
assessment that a technical buyer or reviewer could act on.

TECH CONSTRAINTS — FOLLOW EXACTLY
- Python 3 standard library only for your own tooling: os, subprocess,
  pathlib, json, re, ast.
- To inspect git history, shell out to the `git` CLI via subprocess.
  Do NOT install GitPython or any other package for this.
- Do NOT install, add, or suggest any new framework, ORM, or library
  (no LangChain, no requests, no pandas) unless the TARGET repo itself
  requires it to run ITS OWN test suite — and even then, only inside
  that repo's own isolated environment (venv/node_modules), never
  globally.
- If the target repo's stack is Node/TS, use its own package manager
  and its own lockfile as-is; do not "upgrade" or "fix" dependencies.
- Never modify, commit, push, or write to the target repository. This
  is a READ-ONLY and RUN-TESTS-ONLY assessment. Do not touch git
  remotes. Any test execution happens in an isolated working copy.

WHAT TO INVESTIGATE (use tools/shell commands for each)
1. Structure & architecture: file tree, entry points, module boundaries.
2. Build & tests: detect the stack, install deps into an isolated env,
   run the test suite, capture pass/fail counts and any errors verbatim.
3. Git history signal (this is the core differentiator vs a basic review):
   - `git branch -a` — are there branches with substantial commits that
     never merged to main?
   - `git log --all --oneline` vs `git log main --oneline` — how much
     work exists outside the branch a casual cloner would see?
   - Recency and frequency of commits; single-author vs multi-author.
4. Dependency health: list declared dependencies, flag anything wildly
   out of date or unpinned in a way that risks reproducibility.
5. Code-level signals: rough complexity/size, obvious TODO/FIXME density,
   presence (or absence) of any tests at all, presence of CI config.

OUTPUT FORMAT (JSON, then a short human-readable summary)
{
  "overall_score": 1-10,
  "architecture_score": 1-10,
  "test_health_score": 1-10,
  "hidden_risk_score": 1-10,   // lower = more hidden risk found
  "evidence": [
    {"claim": "...", "source": "file path, command, or log line"}
  ],
  "flags": ["e.g. '40% of total commits live on unmerged branch feature/x'"],
  "confidence": "low|medium|high"
}

RULES
- Every claim in "evidence" must point to something you actually ran or
  read — a file path, a command you executed, or a log excerpt. No
  claims without a source.
- If something can't be verified (e.g. tests won't run at all), say so
  explicitly rather than guessing a score.
- Keep the human-readable summary honest and specific enough that a
  second reviewer could re-run your commands and get the same answer.
```

---

## 5. Building the trap case yourself (this is your strongest eval repo)

Rather than hunting for a public repo with exactly the "hidden branch" pattern, **build one deliberately** — it's synthetic data, which the rules explicitly welcome, and it directly mirrors your Conclave discovery (so it becomes true evidence for your hot take, not just an anecdote).

- On `main`: decent README, a couple of working modules, tests passing.
- On an unmerged branch: a genuinely substantial, working feature (more code than main), never mentioned in the README, never merged.
- Ground truth: this repo is actually *better* than main alone suggests — a README/demo-only review will underrate it; your agent, which checks `git branch -a`, should catch it.

---

## 6. Eval set & rubric (Measured Improvement — 15 pts)

**Pick 6 repos, not 10** — honest scope beats padding given your timeline; note this tradeoff explicitly in your README.

| # | Repo | Why it's in the set |
|---|------|----------------------|
| 1 | APIGuardian (yours) | Known-good, you can sanity-check the agent against ground truth you already understand deeply |
| 2 | An earlier/weaker repo of yours (or a small rough OSS repo) | Known-mediocre, tests thin or missing |
| 3 | Your synthetic "hidden branch" repo (Section 5) | The hard case — this is the one you explain in depth |
| 4–6 | 3 small, real public repos across a quality spread (pick ones under ~2k LOC so tests actually run fast) | Breadth, generalization beyond repos you built |

**Your rubric** (you are the "qualified reviewer" — score each repo yourself, in `eval/repos.md`, *before* running the agent, so you're not anchoring on its output):

| Dimension | 1–10 |
|---|---|
| Architecture clarity | |
| Test health (do tests exist, pass, cover real logic) | |
| Hidden risk (undisclosed branches, stale deps, no CI) | |
| Overall — would you trust/acquire this as-is | |

**Results table** (fill in `eval/results.md`):

| Metric | Baseline | Agent (Provenance) | Your ground truth | Change |
|---|---|---|---|---|
| Rank correlation to your ranking | | | — | |
| Caught the hidden-branch case? | No (can't see it) | ? | Yes | |
| Time per repo | | | | |
| Cost per repo (API/compute) | | | | |

Include **one challenging case with a written explanation** (use the trap repo) — the brief explicitly rewards this.

---

## 7. Changelog — how it actually works

You fill this in **as you build**, not after. Every time you change the agent meaningfully, add a row: what you tried, why, what happened, what you decided. It's your running lab notebook.

```markdown
## Improvement Changelog

| Stage | What I tried & why | Evidence | Decision |
|---|---|---|---|
| Baseline | README + file listing only, single prompt | Scored trap repo 4/10, missed hidden branch entirely | Starting point established |
| Iteration 1 | Added `git branch -a` + `git log --all` inspection, because baseline can't see undisclosed work | Trap repo score moved to 8/10, correctly flagged the unmerged feature | Kept — this is the core differentiator |
| Iteration 2 | Added actual test execution instead of trusting README claims | Caught [repo] claiming "fully tested" with 0 passing tests | Kept |
| Iteration 3 | (example) Tried adding a dependency-vulnerability scanner | Added noise, low signal for repos this small, ate most of the time budget | Removed — document what this taught you |
| Final | Combined git-history check + real test run + evidence-tagged scoring | Rank correlation to my own scoring: [X] vs baseline's [Y] | Main contribution: git-history signal |
```

Keep at least one "removed" row — the brief explicitly wants to see what you tried and cut.

---

## 8. Video script (≤5 min)

**0:00–0:35 — Problem + baseline**
"I'm Jacobs. This is Provenance — an agent that tells you what a codebase is actually worth before you trust it. Here's the problem: a README and a demo tell you almost nothing. On a real project I worked on, a teammate's substantial work sat on an unmerged branch — invisible to anyone who just cloned main. A basic review would never have caught that. Here's the baseline: one prompt, README and file listing only." [show baseline output, low score, generic]

**0:35–3:00 — Live walkthrough**
"Now watch the agent review the same repo." [Screen record: point OpenCode at the trap repo, let it run — show it executing `git branch -a`, running tests, producing the evidence-tagged JSON]. Narrate what it's checking and why as it runs. End on the score + flags, specifically calling out the hidden-branch flag.

**3:00–3:45 — Final comparison**
[Show the results table: baseline vs agent vs your ground truth across all 6 repos] "Across six repos, the agent's ranking matched mine on [X], the baseline matched on [Y]. On the trap repo specifically — the one built to mirror what actually happened to me — baseline scored it a 4, the agent caught the hidden work and scored it an 8, matching my own assessment."

**3:45–4:30 — Changelog highlight**
"The single biggest jump came from adding git-history inspection — that's iteration 1. I also tried a dependency-vulnerability scanner in iteration 3 and cut it — too much noise for repos this size, not worth the time it cost."

**4:30–5:00 — Hot take**
"My takeaway: the biggest quality signal in a codebase is usually the thing nobody thought to look at — not the code that's there, but the work that's invisible by default. Any agent judging a repo needs to actively go looking for what isn't shown, not just evaluate what's presented to it."

---

## 9. Things easy to miss — don't skip these

- **Registration**: confirm you're actually registered on the challenge platform, not just able to see the brief — check today.
- **Capture real trajectories, not just final output.** Configure OpenCode to save full session logs per repo run; you need these raw, not reconstructed after the fact.
- **Sandbox test execution.** You're running arbitrary code's test suite from repos on the internet — do it in an isolated venv/container/throwaway clone, never in a directory with your credentials or SSH keys nearby. This also satisfies ground rule 4.
- **No secrets in the submission** — double check before you push.
- **Disclose your tooling explicitly** in the README: "Agent: OpenCode running MiMo 2.5" — required, not optional.
- **Reproduction guide needs real numbers** — actual runtime and rough cost per repo, not placeholders.

---

## 10. Rough time budget (~24–28 hrs left)

1. Hr 0–2: scaffold repo, write baseline script, build/pick the 6 eval repos (build the trap repo first — everything else depends on it existing)
2. Hr 2–3: score all 6 repos yourself against the rubric (ground truth, before running the agent)
3. Hr 3–8: build the agent + system prompt, get it running end-to-end on ONE repo
4. Hr 8–12: run agent + baseline across all 6 repos, save every trajectory log
5. Hr 12–14: fill in changelog as you recall/redo key iterations, build results table
6. Hr 14–16: write README, reproduction guide
7. Hr 16–18: record video
8. Buffer: leave several hours before the 6PM UTC deadline for submission upload and re-checking the reproduction steps from a clean clone
