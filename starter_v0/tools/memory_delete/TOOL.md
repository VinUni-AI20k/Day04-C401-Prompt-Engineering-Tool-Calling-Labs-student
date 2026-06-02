---
name: memory_delete
track: bonus
kind: local_memory
provider: local_json
requires_env: []
inputs: [name]
outputs: [status, path]
side_effect: true
---
# memory_delete

Deletes a local lab memory record from `starter_v0/memory_store/*.json` by name.
Use only when the user explicitly asks to forget/delete a memory for this lab
agent. This does not delete Claude Code persistent memory.
