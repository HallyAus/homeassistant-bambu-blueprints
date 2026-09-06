# Issue #7 fix acceptance criteria

Temporary implementation note for the fix branch. Delete this file before merge.

The v4.1 progress-threshold path captures the snapshot, then unconditionally waits up to 10 minutes for `print_status_sensor` to transition to `finish`/`failed`. On P1S traces, `finish` can occur briefly during the snapshot/light delay and transition to `idle` before `wait_for_trigger` begins, so the event is missed.

Implement the minimal upstream-safe fix in BOTH identical blueprint copies (`bambu_print_notify.yaml` and `blueprints/automation/danielhall/bambu_print_notify.yaml`): for the progress-threshold path, only enter the finish/fault `wait_for_trigger` while the current print status is still `running`. If it is already `finish`, `failed`, `idle`, or otherwise no longer running, skip the wait and continue to the existing state-settle delay/notification logic. Preserve TTS, cooldown, critical notification, snapshot-light and custom-action features.

Do not use PR #8's mis-indented condition. Keep both blueprint copies byte-for-byte equivalent after the change. Validate YAML/blueprint structure and add a regression check if the repo has a suitable test mechanism.
