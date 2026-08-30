#!/usr/bin/env python3
"""
Agent runner: wires OpenCode/MiMo to the Provenance review tools.

This script orchestrates the agent's investigation of a target repository
by executing shell commands and collecting evidence.
"""

import json
import os
import subprocess
import sys
from pathlib import Path


def run_cmd(cmd: list[str], cwd: str = None) -> dict:
    """Run a shell command and return its output."""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=120,
        )
        return {
            "command": " ".join(cmd),
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {
            "command": " ".join(cmd),
            "stdout": "",
            "stderr": "Command timed out after 120 seconds",
            "returncode": -1,
        }
    except Exception as e:
        return {
            "command": " ".join(cmd),
            "stdout": "",
            "stderr": str(e),
            "returncode": -1,
        }


def investigate_structure(repo_path: str) -> dict:
    """1. Structure & architecture: file tree, entry points, module boundaries."""
    tree = run_cmd(["git", "ls-files"], cwd=repo_path)
    readme = ""
    readme_path = Path(repo_path) / "README.md"
    if readme_path.exists():
        readme = readme_path.read_text(encoding="utf-8", errors="replace")[:2000]
    return {"file_tree": tree["stdout"], "readme_preview": readme}


def investigate_tests(repo_path: str) -> dict:
    """2. Build & tests: detect stack, run test suite."""
    has_requirements = (Path(repo_path) / "requirements.txt").exists()
    has_package_json = (Path(repo_path) / "package.json").exists()
    has_setup_py = (Path(repo_path) / "setup.py").exists()
    has_pyproject = (Path(repo_path) / "pyproject.toml").exists()

    test_result = {"stack": "unknown", "tests_ran": False, "output": ""}

    if has_requirements or has_setup_py or has_pyproject:
        test_result["stack"] = "python"
        # Try to run tests
        venv_path = Path(repo_path) / ".venv_provenance"
        if not venv_path.exists():
            run_cmd([sys.executable, "-m", "venv", str(venv_path)], cwd=repo_path)

        pip = venv_path / "Scripts" / "pip.exe" if os.name == "nt" else venv_path / "bin" / "pip"
        pytest_bin = venv_path / "Scripts" / "pytest.exe" if os.name == "nt" else venv_path / "bin" / "pytest"

        run_cmd([str(pip), "install", "-r", "requirements.txt", "pytest"], cwd=repo_path)
        result = run_cmd([str(pytest_bin), "--tb=short", "-q"], cwd=repo_path)
        test_result["tests_ran"] = True
        test_result["output"] = result["stdout"] + result["stderr"]
    elif has_package_json:
        test_result["stack"] = "node"
        result = run_cmd(["npm", "test"], cwd=repo_path)
        test_result["tests_ran"] = True
        test_result["output"] = result["stdout"] + result["stderr"]

    return test_result


def investigate_git_history(repo_path: str) -> dict:
    """3. Git history signal: branches, commits, recency."""
    branches = run_cmd(["git", "branch", "-a"], cwd=repo_path)
    log_all = run_cmd(["git", "log", "--all", "--oneline"], cwd=repo_path)
    log_main = run_cmd(["git", "log", "main", "--oneline"], cwd=repo_path)
    log_recent = run_cmd(
        ["git", "log", "--all", "--oneline", "--since=6.months"], cwd=repo_path
    )
    authors = run_cmd(
        ["git", "log", "--all", "--format=%an"], cwd=repo_path
    )

    return {
        "branches": branches["stdout"],
        "log_all": log_all["stdout"],
        "log_main": log_main["stdout"],
        "recent_commits": log_recent["stdout"],
        "authors": authors["stdout"],
    }


def investigate_dependencies(repo_path: str) -> dict:
    """4. Dependency health."""
    deps = {}
    req_path = Path(repo_path) / "requirements.txt"
    if req_path.exists():
        deps["requirements.txt"] = req_path.read_text().strip().split("\n")
    pkg_path = Path(repo_path) / "package.json"
    if pkg_path.exists():
        try:
            pkg = json.loads(pkg_path.read_text())
            deps["package.json"] = {
                "dependencies": list(pkg.get("dependencies", {}).keys()),
                "devDependencies": list(pkg.get("devDependencies", {}).keys()),
            }
        except json.JSONDecodeError:
            deps["package.json"] = "Could not parse"
    return deps


def investigate_code_signals(repo_path: str) -> dict:
    """5. Code-level signals: TODO/FIXME, complexity, CI."""
    todo_result = run_cmd(
        ["git", "grep", "-r", "-n", "TODO\\|FIXME", "--", "*.py", "*.js", "*.ts"],
        cwd=repo_path,
    )
    has_ci = (
        (Path(repo_path) / ".github" / "workflows").exists()
        or (Path(repo_path) / ".gitlab-ci.yml").exists()
        or (Path(repo_path) / "Jenkinsfile").exists()
    )
    return {
        "todo_fixme": todo_result["stdout"],
        "has_ci": has_ci,
    }


def generate_agent_prompt(evidence: dict) -> str:
    """Generate the final prompt for the LLM to score the repo."""
    return f"""Based on the following evidence collected from a repository review, produce a JSON assessment.

EVIDENCE:
{json.dumps(evidence, indent=2)}

OUTPUT FORMAT:
{{
  "overall_score": 1-10,
  "architecture_score": 1-10,
  "test_health_score": 1-10,
  "hidden_risk_score": 1-10,
  "evidence": [{{"claim": "...", "source": "..."}}],
  "flags": ["..."],
  "confidence": "low|medium|high"
}}
"""


def run_agent(repo_path: str) -> dict:
    """Run the full agent investigation on a repository."""
    print(f"[*] Investigating: {repo_path}", file=sys.stderr)

    evidence = {
        "structure": investigate_structure(repo_path),
        "tests": investigate_tests(repo_path),
        "git_history": investigate_git_history(repo_path),
        "dependencies": investigate_dependencies(repo_path),
        "code_signals": investigate_code_signals(repo_path),
    }

    prompt = generate_agent_prompt(evidence)
    return {
        "repo_path": repo_path,
        "evidence": evidence,
        "prompt_for_llm": prompt,
        "note": "Evidence collected. Send prompt_for_llm to LLM for final scoring.",
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: python run_agent.py <repo_path>")
        print("\nThis is the Provenance agent runner.")
        print("It investigates a repository and collects evidence for scoring.")
        sys.exit(1)

    repo_path = sys.argv[1]
    if not os.path.isdir(repo_path):
        print(f"Error: {repo_path} is not a directory")
        sys.exit(1)

    result = run_agent(repo_path)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
