---
name: current_time
track: extension
kind: local
requires_env: []
inputs: []
outputs: [current_time, date, day_of_week, iso_timestamp]
side_effect: false
---
# current_time

Returns the current date and time of the system. Very useful for resolving queries requiring relative dates (e.g. "past 24 hours", "yesterday").
