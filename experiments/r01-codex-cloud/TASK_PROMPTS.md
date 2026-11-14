# R01 - Copiable Codex task instructions

## B0 baseline
Within experiments/r01-codex-cloud only, copy shared files to runs/baseline. Read shared/SCENARIO.md and shared/DECISIONS.md. Execute A as written. For B, do not perform an API-breaking field rename without the owner's explicit approval. For C, distinguish decisions needing re-evaluation from those that remain applicable. Write RESULT.md with executed/not-run/blocked states, human approvals requested, exact changed files and evidence. Do not use real APIs or credentials. Do not claim an unexecuted test passed.

## B1 BMad Method 6.12.4
Use a FRESH Codex task. Copy shared to runs/bmad. Install BMad Method 6.12.4 configured for Codex in that folder and record setup. Use its official roles and workflow to handle the SAME tasks A/B/C. Stop at any real owner approval gate. Do not read other experiment results. Record all user interventions and unneeded/missed approvals in runs/bmad/RESULT.md and setup in runs/bmad/SETUP.md.

## B2 OpenSpec 2.0.0
Use a FRESH Codex task. Copy shared to runs/openspec and initialize OpenSpec 2.0.0 for Codex in that folder. Use its proposal, specification delta, tasks and validation for the SAME tasks A/B/C. Never implement the unapproved API rename. Record in runs/openspec/RESULT.md and SETUP.md. Do not read other experiment results.

## B3 GitHub Spec Kit
Use a FRESH Codex task. Copy shared to runs/spec-kit and initialize Spec Kit configured for Codex. Use specify, plan, tasks and analysis workflows for the SAME A/B/C. Record in runs/spec-kit/RESULT.md and SETUP.md. Do not read other experiment results.

After individual experiments, consolidate EVALUATION.md. Maintain the same model and reasoning settings where possible. Distinguish setup from task success, and never infer actual elapsed time or token use.