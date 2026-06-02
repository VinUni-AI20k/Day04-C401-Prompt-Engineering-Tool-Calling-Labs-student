# Person 2 Runbook

Person 2 added one new local research tool:

```text
source_check
```

## Files

- `tools/source_check/TOOL.md`
- `tools/source_check/tool.py`
- `tools/__init__.py`
- `artifacts/tools.yaml`
- `artifacts/system_prompt.md`
- `tests/test_source_check.py`

## What The Tool Does

`source_check` checks a list of research items for:

- duplicate URLs
- invalid URLs
- insecure HTTP links
- missing source labels
- low independent-domain diversity

It has no external API dependency and no side effect.

## Direct Test

Run from `starter_v0/`:

```powershell
python -m unittest discover -s tests -v
```

Expected:

```text
Ran 2 tests
OK
```

## Suggested Eval Case For Person 3

Add a group eval case that asks the agent to check whether a list of collected
research links is ready to cite/publish. Expected tool:

```json
{
  "name": "source_check",
  "args": {
    "min_sources": 2
  }
}
```
