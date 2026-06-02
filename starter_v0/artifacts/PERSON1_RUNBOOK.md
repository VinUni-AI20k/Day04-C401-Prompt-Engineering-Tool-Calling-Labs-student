# Person 1 Runbook

This file records the Person 1 work and the exact commands to finish the
evidence-driven loop after real API keys are added to `.env`.

## Current Blocker

Preflight currently stops at:

```text
RuntimeError: Missing API key env var: OPENROUTER_API_KEY
```

`.env` has been created from `.env.example`. Fill at least:

```text
OPENROUTER_API_KEY=...
TAVILY_API_KEY=...
FIRECRAWL_API_KEY=...
RAPIDAPI_KEY=...
RAPIDAPI_TWITTER_HOST=twitter-api45.p.rapidapi.com
```

## Artifact Changes Already Made

- `artifacts/baseline_system_prompt.md` and `artifacts/baseline_tools.yaml`:
  saved baseline copies for a clean `v0` run after keys are available.
- `artifacts/system_prompt.md`: replaced the intentionally unsafe baseline
  prompt with routing rules for clarify, timeline, social_search, lookup, fetch,
  send confirmation, out-of-scope handling, and multi-turn carryover.
- `artifacts/tools.yaml`: clarified tool descriptions and argument conventions
  without renaming tools.

Static check passed:

```text
declared= ['clarify', 'timeline', 'social_search', 'lookup', 'fetch', 'format', 'send', 'policy', 'papers', 'paper_text']
missing_in_registry= []
expected_not_declared= []
count= 10
```

## Commands To Run After Adding Keys

Run from `starter_v0/`.

```powershell
python scripts/preflight_provider.py --provider openrouter
```

Run baseline `v0` from the saved baseline copies:

```powershell
python run_eval.py --provider openrouter --version v0 --suite base --system-prompt artifacts/baseline_system_prompt.md --tools artifacts/baseline_tools.yaml --eval-cases data/eval_base.json
```

Run the current optimized artifacts as `v1`:

```powershell
python run_eval.py --provider openrouter --version v1 --suite base --eval-cases data/eval_base.json
```

Inspect the saved JSON:

```powershell
Get-ChildItem -LiteralPath .\runs -Filter *.json | Sort-Object LastWriteTime -Descending | Select-Object -First 3
```

Open the latest run JSON and read:

- `summary.case_accuracy`
- `summary.tool_routing_accuracy`
- `summary.argument_accuracy`
- `summary.multiturn_accuracy`
- `summary.failure_counts`
- `summary.observed_mismatch_counts`
- `results[*].result.failures`
- `results[*].result.observed_mismatch`

For v2 and v3, change only one hypothesis at a time in
`artifacts/system_prompt.md` or `artifacts/tools.yaml`, then run:

```powershell
python run_eval.py --provider openrouter --version v2 --suite base --eval-cases data/eval_base.json
python run_eval.py --provider openrouter --version v3 --suite base --eval-cases data/eval_base.json
```

## Suggested Version Log Hypotheses

Use real metric values and real run file paths from `runs/*.json`.

```csv
v0,team,baseline,<artifact_version>,<prompt_hash>,<tools_hash>,baseline,Measure intentionally vague starter behavior before optimization,,<case_accuracy>,<run_file>
v1,team,"system_prompt.md;tools.yaml",<artifact_version>,<prompt_hash>,<tools_hash>,Add routing boundaries and clearer tool declarations,If the model is told not to guess missing accounts/URLs and tool descriptions define source boundaries then routing/argument accuracy should improve,<v0_case_accuracy>,<v1_case_accuracy>,<run_file>
v2,team,<changed_artifact>,<artifact_version>,<prompt_hash>,<tools_hash>,<reason from v1 failures>,<single hypothesis from observed_mismatch>,<v1_case_accuracy>,<v2_case_accuracy>,<run_file>
v3,team,<changed_artifact>,<artifact_version>,<prompt_hash>,<tools_hash>,<reason from v2 failures>,<single hypothesis from observed_mismatch>,<v2_case_accuracy>,<v3_case_accuracy>,<run_file>
```
