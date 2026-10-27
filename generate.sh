#!/usr/bin/env bash
# Rule in, FeatureScript out: asks Claude (Claude Code CLI, headless) to write a checker feature for one rule file.
#   ./generate.sh rules/hole-edge.json > out/HoleEdgeCheck.generated.fs
# Needs the `claude` CLI signed in. Output is a draft: paste it into a Feature Studio and fix what Onshape flags.
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd)
rule=${1:?usage: generate.sh RULE.json}
[[ -f $rule ]] || { echo "no such rule file: $rule" >&2; exit 2; }
command -v claude >/dev/null || { echo "claude CLI not found (npm i -g @anthropic-ai/claude-code)" >&2; exit 2; }
prompt="$(cat "$here/prompts/rule-to-featurescript.md")

Rule:
$(cat "$rule")"
claude -p --model "${MODEL:-sonnet}" "$prompt"
