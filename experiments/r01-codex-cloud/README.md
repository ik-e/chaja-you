# R01 - Codex Cloud experiment

Purpose: measure human supervision burden when comparing Codex alone, BMad, OpenSpec, and Spec Kit under the SAME mock-project scenario.
Scope: experiment branch ONLY. Do not change main, team deliverables, real services, or files outside experiments/r01-codex-cloud.

## Sign in and run

1. Open https://chatgpt.com/codex while logged into the intended ChatGPT account.
2. Connect GitHub repository ik-e/chaja-you when prompted.
3. Select the branch experiment/r01-codex-cloud-20261114.
4. Ask Codex to read experiments/r01-codex-cloud/HANDOFF.md first, then TASK_PROMPTS.md, and execute task B0 only.
5. Use a fresh task or worktree for each comparator, so it does not inherit the earlier product output.

Do not paste tokens, auth cookies or device codes into this repository or chat. Never activate credit purchases or optional paid upgrades.

## Setup comparisons

B0: Codex without workflow framework.
B1: BMad Method 6.12.4 for Codex, installed in isolated runs/bmad.
B2: OpenSpec 2.0.0 for Codex, installed in isolated runs/openspec.
B3: Spec Kit official CLI for Codex, installed in isolated runs/spec-kit.
B4: Bathos v0.4.0 is a later comparison in its default Claude Code runtime; Vercel lab has a compiled binary but no model auth.

Start with HANDOFF.md (context from a separate ChatGPT session), then TASK_PROMPTS.md, shared/SCENARIO.md and EVALUATION.md.

This GitHub branch was created in advance; no actual Codex Cloud task has yet been run.