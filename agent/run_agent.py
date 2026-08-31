#!/usr/bin/env python3
"""
Agent runner: wires Groq LLM to the Provenance review tools.

This script orchestrates the agent's investigation of a target repository
by executing shell commands and collecting evidence, then calls Groq API
to produce a scored assessment.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

try:
    from groq import Groq
except ImportError:
    print("Error: groq package not installed. Run: pip install groq", file=sys.stderr)
    sys.exit(1)


def run_cmd(cmd: list, cwd: str = None) -> dict:
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
        
        # Check for existing venv first, then create if needed
        venv_path = Path(repo_path) / ".venv_provenance"
        existing_venv = Path(repo_path) / "venv"
        
        if existing_venv.exists() and (existing_venv / "Scripts" / "pytest.exe").exists():
            venv_path = existing_venv
        elif not venv_path.exists():
            run_cmd([sys.executable, "-m", "venv", str(venv_path)], cwd=repo_path)

        pip = venv_path / "Scripts" / "pip.exe" if os.name == "nt" else venv_path / "bin" / "pip"
        pytest_bin = venv_path / "Scripts" / "pytest.exe" if os.name == "nt" else venv_path / "bin" / "pytest"

        if pip.exists():
            run_cmd([str(pip), "install", "-r", "requirements.txt", "pytest", "-q"], cwd=repo_path)
        
        if pytest_bin.exists():
            result = run_cmd([str(pytest_bin), "--tb=short", "-q"], cwd=repo_path)
            test_result["tests_ran"] = True
            test_result["output"] = result["stdout"] + result["stderr"]
        else:
            test_result["output"] = "pytest not found in venv"
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
    log_main = run_cmd(["git", "log", "master", "--oneline"], cwd=repo_path)
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


def call_groq(prompt: str) -> str:
    """Call Groq API to score the repository."""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return json.dumps({"error": "GROQ_API_KEY environment variable not set"})

    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model="qwen/qwen3.8-27b",
        messages=[
            {"role": "system", "content": "You are a code repository reviewer. Output only valid JSON."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=1000,
    )
    return response.choices[0].message.content


def format_txt_output(scores: dict, evidence: dict, repo_path: str) -> str:
    """Format a clean .txt diagnosis file."""
    lines = []
    lines.append("=" * 60)
    lines.append("PROVENANCE - Full Agent Repository Review")
    lines.append("=" * 60)
    lines.append(f"\nRepository: {repo_path}")
    lines.append(f"Review Type: Full Agent (git history + tests + dependencies)")
    lines.append("")

    if "error" in scores:
        lines.append("ERROR:")
        lines.append(scores["error"])
        return "\n".join(lines)

    lines.append("SCORES")
    lines.append("-" * 40)
    lines.append(f"Overall Score:        {scores.get('overall_score', 'N/A')}/10")
    lines.append(f"Architecture Score:   {scores.get('architecture_score', 'N/A')}/10")
    lines.append(f"Test Health Score:    {scores.get('test_health_score', 'N/A')}/10")
    lines.append(f"Hidden Risk Score:    {scores.get('hidden_risk_score', 'N/A')}/10")
    lines.append("")

    lines.append("EVIDENCE")
    lines.append("-" * 40)
    for item in scores.get("evidence", []):
        lines.append(f"- {item.get('claim', 'N/A')}")
        lines.append(f"  Source: {item.get('source', 'N/A')}")
    lines.append("")

    lines.append("FLAGS")
    lines.append("-" * 40)
    for flag in scores.get("flags", []):
        lines.append(f"! {flag}")
    lines.append("")

    lines.append("CONFIDENCE")
    lines.append("-" * 40)
    lines.append(f"Level: {scores.get('confidence', 'N/A')}")
    lines.append("")

    lines.append("INVESTIGATION DETAILS")
    lines.append("-" * 40)

    # Git history
    git = evidence.get("git_history", {})
    branches = git.get("branches", "").strip()
    if branches:
        lines.append("\nBranches found:")
        for b in branches.split("\n"):
            lines.append(f"  {b.strip()}")

    # Tests
    tests = evidence.get("tests", {})
    lines.append(f"\nTest execution: {'Yes' if tests.get('tests_ran') else 'No'}")
    if tests.get("output"):
        output_lines = tests["output"].strip().split("\n")[:10]
        lines.append("Test output (first 10 lines):")
        for line in output_lines:
            lines.append(f"  {line}")

    # Dependencies
    deps = evidence.get("dependencies", {})
    if deps:
        lines.append("\nDependencies found:")
        for key, val in deps.items():
            if isinstance(val, list):
                lines.append(f"  {key}: {len(val)} packages")
            else:
                lines.append(f"  {key}: {val}")

    # Code signals
    signals = evidence.get("code_signals", {})
    lines.append(f"\nCI configured: {'Yes' if signals.get('has_ci') else 'No'}")
    todo = signals.get("todo_fixme", "").strip()
    if todo:
        lines.append(f"TODO/FIXME items: {len(todo.split(chr(10)))} found")

    lines.append("")
    lines.append("=" * 60)
    lines.append("END OF REPORT")
    lines.append("=" * 60)

    return "\n".join(lines)


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

    # Call Groq API to get scored assessment
    print("[*] Calling LLM for scoring...", file=sys.stderr)
    response = call_groq(prompt)

    # Strip markdown code blocks if present
    cleaned = response.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    if cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    cleaned = cleaned.strip()

    try:
        scores = json.loads(cleaned)
    except json.JSONDecodeError:
        scores = {"error": "Failed to parse LLM response", "raw_response": response}

    return {
        "repo_path": repo_path,
        "scores": scores,
        "evidence": evidence,
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: python run_agent.py <repo_path>")
        print("\nThis is the Provenance agent runner.")
        print("It investigates a repository and produces a scored assessment.")
        print("\nRequired environment variable: GROQ_API_KEY")
        sys.exit(1)

    repo_path = sys.argv[1]
    if not os.path.isdir(repo_path):
        print(f"Error: {repo_path} is not a directory")
        sys.exit(1)

    result = run_agent(repo_path)

    # Write JSON output
    json_path = Path(repo_path) / "agent_review.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    print(f"JSON output: {json_path}")

    # Write .txt output
    txt_content = format_txt_output(result["scores"], result["evidence"], repo_path)
    txt_path = Path(repo_path) / "agent_review.txt"
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(txt_content)
    print(f"TXT output: {txt_path}")

    # Also print JSON to stdout
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
