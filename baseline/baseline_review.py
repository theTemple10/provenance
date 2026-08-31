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

try:
    from groq import Groq
except ImportError:
    print("Error: groq package not installed. Run: pip install groq", file=sys.stderr)
    sys.exit(1)


def read_readme(repo_path: str) -> str:
    """Read the README file from a repository."""
    readme_path = Path(repo_path) / "README.md"
    if readme_path.exists():
        return readme_path.read_text(encoding="utf-8", errors="replace")
    for alt in ["readme.md", "Readme.md", "README.rst", "README.txt"]:
        alt_path = Path(repo_path) / alt
        if alt_path.exists():
            return alt_path.read_text(encoding="utf-8", errors="replace")
    return "[No README found]"


def get_file_tree(repo_path: str, max_depth: int = 2) -> str:
    """Get a simple file tree listing."""
    tree_lines = []
    repo = Path(repo_path)
    skip_dirs = {".git", "__pycache__", "node_modules", ".venv", "venv", ".env", ".venv_provenance"}

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
{readme[:3000]}

--- FILE TREE ---
{file_tree}
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
        max_tokens=500,
    )
    return response.choices[0].message.content


def format_txt_output(result: dict, repo_path: str) -> str:
    """Format a clean .txt diagnosis file."""
    lines = []
    lines.append("=" * 60)
    lines.append("PROVENANCE - Baseline Repository Review")
    lines.append("=" * 60)
    lines.append(f"\nRepository: {repo_path}")
    lines.append(f"Review Type: Baseline (README + file tree only)")
    lines.append("")

    if "error" in result:
        lines.append("ERROR:")
        lines.append(result["error"])
        return "\n".join(lines)

    lines.append("SCORES")
    lines.append("-" * 40)
    lines.append(f"Overall Score:      {result.get('overall_score', 'N/A')}/10")
    lines.append("")

    lines.append("ARCHITECTURE ASSESSMENT")
    lines.append("-" * 40)
    lines.append(result.get("architecture_note", "No assessment provided"))
    lines.append("")

    lines.append("RISK ASSESSMENT")
    lines.append("-" * 40)
    lines.append(result.get("risk_note", "No assessment provided"))
    lines.append("")

    lines.append("CONFIDENCE")
    lines.append("-" * 40)
    lines.append(f"Level: {result.get('confidence', 'N/A')}")
    lines.append("(Always low for baseline - limited evidence)")
    lines.append("")

    lines.append("=" * 60)
    lines.append("NOTE: This is a baseline review with limited information.")
    lines.append("For a comprehensive assessment, use the full agent review.")
    lines.append("=" * 60)

    return "\n".join(lines)


def run_baseline(repo_path: str) -> dict:
    """Run the baseline review on a repository."""
    readme = read_readme(repo_path)
    file_tree = get_file_tree(repo_path)
    prompt = build_baseline_prompt(readme, file_tree)

    # Call Groq API to get scored assessment
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
        "readme_length": len(readme),
        "file_tree_lines": len(file_tree.split("\n")),
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: python baseline_review.py <repo_path>")
        print("\nThis is the baseline reviewer.")
        print("It generates a prompt from README + file tree only.")
        print("No git history, no test execution, no dependency analysis.")
        print("\nRequired environment variable: GROQ_API_KEY")
        sys.exit(1)

    repo_path = sys.argv[1]
    if not os.path.isdir(repo_path):
        print(f"Error: {repo_path} is not a directory")
        sys.exit(1)

    result = run_baseline(repo_path)

    # Write JSON output
    json_path = Path(repo_path) / "baseline_review.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    print(f"JSON output: {json_path}")

    # Write .txt output
    txt_content = format_txt_output(result["scores"], repo_path)
    txt_path = Path(repo_path) / "baseline_review.txt"
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(txt_content)
    print(f"TXT output: {txt_path}")

    # Also print JSON to stdout
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
