#!/usr/bin/env python3
"""
Baseline reviewer: dumb version - README + file tree only, single LLM prompt.

No git history, no test execution, no dependency analysis.
This is the "one direct prompt with basic instructions" baseline
per the hackathon brief.
"""

import json
import os
import sys
from pathlib import Path


def read_readme(repo_path: str) -> str:
    """Read the README file from a repository."""
    readme_path = Path(repo_path) / "README.md"
    if readme_path.exists():
        return readme_path.read_text(encoding="utf-8", errors="replace")
    # Try alternative README filenames
    for alt in ["readme.md", "Readme.md", "README.rst", "README.txt"]:
        alt_path = Path(repo_path) / alt
        if alt_path.exists():
            return alt_path.read_text(encoding="utf-8", errors="replace")
    return "[No README found]"


def get_file_tree(repo_path: str, max_depth: int = 2) -> str:
    """Get a simple file tree listing."""
    tree_lines = []
    repo = Path(repo_path)
    skip_dirs = {".git", "__pycache__", "node_modules", ".venv", "venv", ".env"}

    def walk(path: Path, prefix: str = "", depth: int = 0):
        if depth > max_depth:
            return
        try:
            entries = sorted(path.iterdir(), key=lambda p: (p.is_file(), p.name))
        except PermissionError:
            return
        for entry in entries:
            if entry.name in skip_dirs:
                continue
            rel = entry.relative_to(repo)
            if entry.is_dir():
                tree_lines.append(f"{prefix}{entry.name}/")
                walk(entry, prefix + "  ", depth + 1)
            else:
                tree_lines.append(f"{prefix}{entry.name}")

    walk(repo)
    return "\n".join(tree_lines)


def build_baseline_prompt(readme: str, file_tree: str) -> str:
    """Build the baseline review prompt."""
    return f"""You are reviewing a code repository to assess its quality for someone
considering acquiring or trusting it.

You are given ONLY:
- The README contents
- A top-level file/folder listing

You do NOT have access to run tests, read git history, or inspect
individual files beyond what's shown.

Based only on this, output a JSON object:
{{
  "overall_score": 1-10,
  "architecture_note": "...",
  "risk_note": "...",
  "confidence": "low" (always say low — you have limited evidence)
}}

--- README CONTENTS ---
{readme}

--- FILE TREE ---
{file_tree}
"""


def run_baseline(repo_path: str) -> dict:
    """Run the baseline review on a repository."""
    readme = read_readme(repo_path)
    file_tree = get_file_tree(repo_path)
    prompt = build_baseline_prompt(readme, file_tree)

    # For now, return the prompt that would be sent to the LLM
    # In actual use, this would call the LLM API
    return {
        "repo_path": repo_path,
        "prompt": prompt,
        "readme_length": len(readme),
        "file_tree_lines": len(file_tree.split("\n")),
        "note": "This is the baseline prompt. In production, send to LLM for scoring.",
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: python baseline_review.py <repo_path>")
        print("\nThis is the baseline reviewer.")
        print("It generates a prompt from README + file tree only.")
        print("No git history, no test execution, no dependency analysis.")
        sys.exit(1)

    repo_path = sys.argv[1]
    if not os.path.isdir(repo_path):
        print(f"Error: {repo_path} is not a directory")
        sys.exit(1)

    result = run_baseline(repo_path)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
