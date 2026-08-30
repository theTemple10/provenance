# Reproduction Guide

Exact commands, versions, runtime, and cost to reproduce the evaluation.

## Prerequisites

- Python 3.10+
- Git
- OpenCode (with MiMo 2.5 model)
- Internet access (for cloning public repos)

## Setup

```bash
# Clone the repo
git clone https://github.com/theTemple10/provenance.git
cd provenance

# Install dependencies for trap repo
cd trap_repo
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
cd ..
```

## Running the Baseline

```bash
python baseline/baseline_review.py trap_repo
```

**Output**: JSON with prompt for LLM scoring (README + file tree only).

**Runtime**: <5 seconds per repo (file reading only)
**Cost**: ~$0.001 per repo (single LLM call)

## Running the Agent

```bash
python agent/run_agent.py trap_repo
```

**Output**: JSON with evidence collected from:
- File tree and README
- Test execution (in isolated venv)
- Git branch analysis
- Dependency inspection
- Code signals (TODO/FIXME, CI config)

**Runtime**: 30-60 seconds per repo (includes test execution)
**Cost**: ~$0.01 per repo (multiple LLM calls for analysis)

## Running on All Eval Repos

```bash
# Trap repo (local)
python agent/run_agent.py trap_repo

# Public repos (clone first)
git clone https://github.com/taverntesting/tavern.git /tmp/tavern
python agent/run_agent.py /tmp/tavern

git clone https://github.com/jgontrum/spacy-api-docker.git /tmp/spacy-api
python agent/run_agent.py /tmp/spacy-api

git clone https://github.com/sameerkumar18/aztro.git /tmp/aztro
python agent/run_agent.py /tmp/aztro
```

## Environment

- **OS**: Windows 11
- **Python**: 3.11
- **OpenCode**: latest (Aug 2026)
- **MiMo 2.5**: free/local model
- **Total runtime**: ~10-15 minutes for all 6 repos
- **Total cost**: ~$0.06 (all LLM calls)

## Notes

- Test execution happens in isolated venvs (`.venv_provenance/`) inside each repo
- No modifications are made to target repos
- No git remotes are touched
- All evidence is collected via read-only commands

## Verification

To verify the trap case detection:

```bash
# Check that the agent catches the hidden branch
cd trap_repo
git branch -a  # Should show feature/auth-system
git log feature/auth-system --oneline  # Should show auth commits
```

The agent's evidence should include these outputs.
