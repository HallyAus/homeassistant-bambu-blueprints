# Bambu Printer Notification Blueprint

Home Assistant automation blueprint for Bambu Lab printers (e.g. P1S, X1C)
using the official Bambu integration.

This blueprint sends mobile notifications when a print **finishes** or
**faults**, including a camera snapshot and optional critical alerts for faults.

## Features

- Finish notification with:
  - Printer name
  - Task name / job name
  - Reported weight
  - Progress
  - Camera snapshot

- Fault notification with:
  - Optional **critical** sound window (e.g. 07:00–21:00)
  - Snapshot of the print at time of failure
  - Persistent notification in Home Assistant

- Guards to reduce noise:
  - Only triggers if progress > 0
  - Only triggers from meaningful stages (printing / inspecting_first_layer / auto_bed_leveling)
  - Per-printer `input_boolean` to enable/disable notifications
  - Cooldown between alerts (default 5 minutes)

- Extras:
  - Uses the Bambu "Force refresh data" button before snapshot
  - Mobile notification action button to open a printers Lovelace view
  - Reuses a single notification tag per printer so the latest state replaces the old one

## Installation

1. Copy `blueprints/automation/danielhall/bambu_print_notify.yaml` into the
   same path in your Home Assistant `config` directory, or import it by URL:

   - Raw URL (example):

     ```
     https://raw.githubusercontent.com/<your_username>/homeassistant-bambu-blueprints/main/blueprints/automation/danielhall/bambu_print_notify.yaml
     ```

2. In Home Assistant, go to:

   **Settings → Automations & Scenes → Blueprints → Import Blueprint**

3. Paste the raw URL and import.

## Creating an automation from the blueprint

Create a new automation using this blueprint and map:

- **Print status sensor**  
  `sensor.<printer>_print_status` (values: running, finish, failed, etc.)

- **Print error binary**  
  `binary_sensor.<printer>_print_error`

- **Current stage sensor**  
  `sensor.<printer>_current_stage`

- **Progress sensor**  
  `sensor.<printer>_print_progress` (%)

- **Printer name sensor**  
  `sensor.<printer>_printer_name`

- **Task name sensor**  
  `sensor.<printer>_task_name`

- **Print weight sensor**  
  `sensor.<printer>_print_weight` (g)

- **Camera**  
  `camera.<printer>_camera`

- **Force refresh button**  
  `button.<printer>_force_refresh_data`

- **Notifications enabled boolean**  
  e.g. `input_boolean.<printer>_notifications_enabled`

- **Notify service**  
  e.g. `notify.mobile_app_your_phone`

- **Snapshot file / URL**  
  - File: `/config/www/snapshots/<printer>_notify.jpg`
  - URL: `/local/snapshots/<printer>_notify.jpg`

- **Critical window**  
  Default: 07:00–21:00 (local time)

- **Cooldown**  
  Default: 5 minutes between alerts

- **Printers view URI (optional)**  
  Example: `/lovelace/3d_printers`

Repeat this blueprint instance per printer (P1S-1, P1S-2, etc.) with the
correct entities and snapshot paths.

## Notes

- The snapshot directory `/config/www/snapshots` must exist.
- `/config/www/...` is exposed by Home Assistant as `/local/...` for the app.
- Critical alerts require that you grant Critical Alerts permission to the Home
  Assistant Companion App in your phone’s OS settings.

Contributions and issues are welcome.
