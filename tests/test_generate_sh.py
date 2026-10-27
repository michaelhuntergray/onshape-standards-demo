"""Regression test for review round 5: `./generate.sh rules/hole-edge.json` must assemble its prompt and call claude.

A stub `claude` on PATH records the prompt it receives, so no network or sign-in is needed.
"""
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def run_generate(tmp_path, rule_arg):
    stub = tmp_path / "bin" / "claude"
    stub.parent.mkdir()
    stub.write_text('#!/usr/bin/env bash\nprintf "%s" "${@: -1}" > "$PROMPT_OUT"\necho STUB-OK\n')
    stub.chmod(0o755)
    out = tmp_path / "prompt.txt"
    env = {**os.environ, "PATH": f"{stub.parent}:{os.environ['PATH']}", "PROMPT_OUT": str(out)}
    res = subprocess.run(["./generate.sh", rule_arg], cwd=ROOT, env=env, capture_output=True, text=True)
    return res, out


def test_documented_invocation_reaches_claude_with_prompt_and_rule(tmp_path):
    res, out = run_generate(tmp_path, "rules/hole-edge.json")
    assert res.returncode == 0, res.stderr
    assert "STUB-OK" in res.stdout
    prompt = out.read_text()
    assert (ROOT / "prompts" / "rule-to-featurescript.md").read_text().strip() in prompt
    assert "\nRule:\n" in prompt
    assert (ROOT / "rules" / "hole-edge.json").read_text().strip() in prompt


def test_missing_rule_file_exits_2(tmp_path):
    res, _ = run_generate(tmp_path, "rules/nope.json")
    assert res.returncode == 2
