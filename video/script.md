# Video Script (≤5 min)

## 0:00–0:35 — Problem + baseline

"I'm Jacobs. This is Provenance — an agent that tells you what a codebase is actually worth before you trust it.

Here's the problem: a README and a demo tell you almost nothing. On a real project I worked on, a teammate's substantial work sat on an unmerged branch — invisible to anyone who just cloned main. A basic review would never have caught that.

Here's the baseline: one prompt, README and file listing only."

[Show baseline output: low score, generic assessment]

---

## 0:35–3:00 — Live walkthrough

"Now watch the agent review the same repo."

[Screen record: point OpenCode at the trap repo, let it run]

**Narrate as it runs:**

"It's checking the file structure — standard Flask app, looks simple.

Now it's running `git branch -a` — and there it is. A `feature/auth-system` branch with substantial commits that never merged to main. The baseline can't see this.

It's running the test suite in an isolated venv — 15 tests pass on main.

Now it's checking the auth branch — 20+ more tests pass. JWT authentication, user roles, middleware. This is real, working code.

It's producing the final score with evidence — every claim points to a command it ran or a file it read."

[End on the score + flags, specifically the hidden-branch flag]

---

## 3:00–3:45 — Final comparison

[Show the results table: baseline vs agent vs ground truth across all 6 repos]

"Across six repos, the agent's ranking matched mine on [X], the baseline matched on [Y].

On the trap repo specifically — the one built to mirror what actually happened to me — baseline scored it a 4, the agent caught the hidden work and scored it an 8, matching my own assessment."

---

## 3:45–4:30 — Changelog highlight

"The single biggest jump came from adding git-history inspection — that's iteration 1.

I also tried a dependency-vulnerability scanner in iteration 3 and cut it — too much noise for repos this size, not worth the time it cost."

[Show CHANGELOG.md with the iteration table]

---

## 4:30–5:00 — Hot take

"My takeaway: the biggest quality signal in a codebase is usually the thing nobody thought to look at — not the code that's there, but the work that's invisible by default.

Any agent judging a repo needs to actively go looking for what isn't shown, not just evaluate what's presented to it."

---

## Production Notes

- **Recording tool**: OBS Studio or similar
- **Screen recording**: Full screen, 1080p
- **Audio**: Clear narration, no background music
- **Editing**: Minimal — just trim dead air, add section titles
- **Total runtime**: 4:30-5:00
