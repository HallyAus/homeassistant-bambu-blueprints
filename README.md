# Bambu Printer Notification Blueprint for Home Assistant

[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-support-yellow?style=for-the-badge&logo=buy-me-a-coffee)](https://buymeacoffee.com/printforge)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2024.6%2B-blue?style=for-the-badge&logo=home-assistant)](https://www.home-assistant.io/)
[![License](https://img.shields.io/badge/License-CC0--1.0-green?style=for-the-badge)](LICENSE)

A powerful Home Assistant blueprint that sends mobile notifications with camera snapshots when your Bambu printer finishes or encounters a fault. Packed with features for the ultimate 3D printing notification experience.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📸 **Smart Snapshots** | Captures a photo near completion at a configurable progress threshold |
| 💡 **Snapshot Lighting** | Optionally turn on a light before capture for better photos |
| 📱 **Mobile Notifications** | Rich notifications with images to iOS/Android |
| 🔊 **TTS Announcements** | Voice announcements on your smart speakers |
| 🚨 **Critical Alerts** | Optional critical notifications that bypass Do Not Disturb |
| ⚡ **Custom Actions** | Run any automation on success or fault |
| 🌙 **Quiet Hours** | Suppress TTS during sleeping hours |
| ⏱️ **Cooldown** | Prevent notification spam |
| 🔔 **Persistent Alerts** | Fault notifications stay until acknowledged |

---

## 📋 Requirements

- Home Assistant **2024.6.0** or newer
- [Bambu Lab integration](https://github.com/greghesp/ha-bambulab) installed and configured
- A camera entity for your printer
- (Optional) Mobile app for push notifications
- (Optional) Media player for TTS announcements

---

## 🚀 Installation

### Method 1: Manual Installation

1. Download [`bambu_print_notify.yaml`](blueprints/automation/danielhall/bambu_print_notify.yaml)
2. Copy to your Home Assistant config:
   ```
   /config/blueprints/automation/custom/bambu_print_notify.yaml
   ```
3. Restart Home Assistant or reload automations

### Method 2: Import via URL

1. Go to **Settings** → **Automations & Scenes** → **Blueprints**
2. Click **Import Blueprint**
3. Paste the raw GitHub URL - https://raw.githubusercontent.com/HallyAus/homeassistant-bambu-blueprints/refs/heads/main/blueprints/automation/danielhall/bambu_print_notify.yaml
4. Click **Preview** then **Import**

Create `/config/www/snapshots/` before enabling the automation, and allow camera
snapshots to be written there in `configuration.yaml` (merge this into your existing
`homeassistant:` configuration):

```yaml
homeassistant:
  allowlist_external_dirs:
    - /config/www/snapshots
```

Validate configuration and restart Home Assistant if you changed this setting.
Files under `/config/www` are served through `/local` without authentication;
only use a camera whose snapshots you are comfortable exposing this way.

### Updating an existing automation

Re-import the blueprint, or replace the YAML at the **same path** referenced by
your automation and reload automations. Both YAML copies in this repository are
identical. Existing inputs retain their names and defaults.

- Existing legacy mobile services continue to work, with or without `notify.`.
- For a notify entity, clear **Legacy notify service** and select **Notify entities**.
- When using `tts.speak`, select your **TTS engine** (for example `tts.piper`).
- Set the progress threshold to `100` if you only want a snapshot at finish/fault.

---

## ⚙️ Configuration

### Required Inputs

| Input | Description |
|-------|-------------|
| **Print status sensor** | Sensor with states: `running`, `finish`, `failed` |
| **Print error binary sensor** | Binary sensor that turns ON on error |
| **Current stage sensor** | Enum sensor for printer stage |
| **Progress sensor** | Print progress percentage |
| **Printer name sensor** | Your printer's name |
| **Task name sensor** | Current print job name |
| **Print weight sensor** | Print weight in grams |
| **Camera** | Your printer's camera entity |
| **Notifications enabled** | input_boolean to enable/disable |

### Snapshot Settings

| Input | Default | Description |
|-------|---------|-------------|
| **Snapshot light** | *none* | Light to turn on before capture |
| **Light brightness** | 100% | Brightness for snapshot light |
| **Snapshot delay** | 1 sec | Delay for light warmup / camera adjustment |

### TTS Settings

| Input | Default | Description |
|-------|---------|-------------|
| **Enable TTS** | Off | Enable voice announcements |
| **TTS service** | `tts.speak` | Your TTS service (google, cloud, piper, etc.) |
| **TTS engine** | none | Required entity for `tts.speak`, such as `tts.piper` |
| **Media player** | *none* | Speaker(s) for announcements |
| **Volume** | 0 (current) | Announcement volume (1-100%) |
| **Success message** | *"{{printer_name}} has finished printing {{task_name}}"* | Customizable template |
| **Fault message** | *"Warning! {{printer_name}} has encountered a fault..."* | Customizable template |
| **Quiet hours** | Off | Suppress TTS during specified times |

### Notification Settings

| Input | Default | Description |
|-------|---------|-------------|
| **Legacy notify service** | *empty* | `mobile_app_*` or `notify.mobile_app_*`; supports rich mobile payloads |
| **Notify entities** | *empty* | One or more `notify.*` entities; title and message only |
| **Success type** | Normal | Normal, Critical, or Never Critical |
| **Fault type** | Critical | Normal, Critical, or Never Critical |
| **Critical sound** | default | iOS sound name |
| **Critical volume** | 1.0 | Alert volume (0.0-1.0) |

Notify entities use [`notify.send_message`](https://www.home-assistant.io/integrations/notify/).
To retain compatibility with Home Assistant 2024.6, this path sends only a title
and message. Snapshots, critical sounds, tags, sticky alerts and action buttons
require the legacy mobile service. Configure both paths only if you want both
to receive a message; the blueprint never falls back to the broadcast `notify.notify`.

### Custom Actions

You can run **any** Home Assistant actions on print success or fault:

**Success action examples:**
- Turn on a green "print done" light
- Power on a cooling fan via smart plug
- Send a message to Discord/Slack
- Turn off the printer after a delay

**Fault action examples:**
- Turn on a red warning light
- Flash lights to get attention
- Pause other printers in your farm
- Send urgent alerts to multiple services

---

## 📝 Template Variables

Use these in your TTS messages:

| Variable | Description | Example |
|----------|-------------|---------|
| `{{ printer_name }}` | Printer name | "X1 Carbon" |
| `{{ task_name }}` | Print job name | "benchy.3mf" |
| `{{ print_weight }}` | Weight in grams | "15" |
| `{{ progress }}` | Progress percentage | "100" |
| `{{ status }}` | Current status | "finish" |

---

## 💡 Tips & Tricks

### Capture Better Snapshots

1. The trigger fires **above** the threshold: `98` usually captures at `99%`,
   while `99` usually captures at `100%`. Bed position depends on the printer's
   reporting; a pre-drop capture is not guaranteed.
2. Add a **snapshot light** for consistent lighting
3. Use a **1-2 second delay** to let the camera adjust

### Critical Notifications

- Set time windows to only get critical alerts during certain hours
- Set **start and end to the same time** for critical alerts all day
- Use "Never Critical" option to always get normal notifications

### Quiet Hours for TTS

Perfect for overnight prints:
- TTS quiet hours: 22:00 → 07:00
- You'll still get mobile notifications, just no voice announcements

### Multiple Printers

Create a separate automation from this blueprint for each printer. Use different:
- Notification tags and snapshot filenames (automatic based on automation entity ID)
- Snapshot lights
- TTS messages

---

## 🐛 Troubleshooting

### "Source not found" when importing

This happens when trying to reimport from a URL. Instead:
1. Download the YAML file manually
2. Place it in `/config/blueprints/automation/custom/`
3. Restart Home Assistant

### Snapshots not saving

1. Ensure `/config/www/snapshots/` directory exists
2. Check Home Assistant has write permissions
3. Verify your camera entity is working

### TTS not working

1. Verify your TTS service name is correct
2. Test your media player with Developer Tools → Services
3. Check you're not in quiet hours

### Notifications not arriving

1. Verify `notify.mobile_app_*` service exists
2. Check the notifications enabled boolean is ON
3. Review cooldown settings

If a `notify.*` entity exists but the matching action does not, select it under
**Notify entities**, not **Legacy notify service**. A missing optional action is
reported in the automation trace; other delivery branches still run.

### Timing and failure behaviour

- A progress-triggered run captures a snapshot, then waits up to ten minutes for
  `finish`, `failed`, `idle`, or an active print-error sensor. It checks the current
  state immediately, so a finish during snapshot capture is not missed. `idle`
  after the near-complete progress trigger is treated as completion because some
  printers report `finish` only briefly.
- Paused, running and unavailable states do not produce a success on timeout.
- Only one run is active at a time. Additional triggers during capture, waiting
  or custom actions are ignored, preventing duplicate photos and notifications.
- Cooldown is measured from the start of the previous run and applies to both
  success and fault triggers. Set it to zero if every separate event is needed.
- Notification channels, TTS and custom actions run independently after capture;
  an unavailable optional service does not block the other branches.
- Snapshot errors appear in the trace but do not block text alerts. Check the
  camera and directory permissions if an image is missing or stale.

## Development and validation

Use Python 3.12 for the minimum-supported-version test suite:

```sh
python -m pip install -r requirements-test.txt
python -m pytest -q
```

Tests import the blueprint and execute real Home Assistant automation triggers,
conditions, templates and actions using synthetic entities and service handlers.
They do not contact a printer or send real notifications. CI also checks that
both import paths contain identical YAML, on Home Assistant 2024.6.0 and 2026.9.3.

---

## 📜 Changelog

### v4.2

- Fix #7: check current completion state after snapshots and prevent queued duplicates.
- Fix #12: add an explicit notify entity selector while preserving legacy rich notifications.
- Correct TTS engine targeting, template evaluation order, cooldown tracking and zero-progress fault handling.
- Refresh status/progress at delivery time, preserve initial fault evidence, and isolate delivery failures.
- Use safe per-automation snapshot filenames with cache-busting URLs.
- Add Home Assistant regression tests, CI and corrected import/setup instructions.

### v4
- ✨ Added TTS announcements with customizable messages
- ✨ Added TTS quiet hours
- ✨ Support for multiple TTS services

### v3
- ✨ Added custom actions on success/fault
- 🎨 Organized inputs into collapsible sections

### v2
- ✨ Added optional snapshot light with brightness control
- 🐛 Fixed critical notifications (now truly optional)
- 🐛 Fixed snapshot delay (positive values only)
- 🐛 Fixed time window handling (00:00-00:00 = disabled)

### v1
- 🎉 Initial release

---

## 🤝 Contributing

Found a bug? Have a feature request? Feel free to:
1. Open an issue
2. Submit a pull request
3. Share your custom configurations

---
## Contributors

- [@sawokei](https://github.com/sawokei) - Bug reports and testing

---

## ☕ Support

If this blueprint has helped you, consider buying me a coffee!

[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-support-yellow?style=for-the-badge&logo=buy-me-a-coffee)](https://buymeacoffee.com/printforge)

Your support helps me create more useful Home Assistant blueprints and integrations.

---

## 📄 License

This project uses CC0 1.0 Universal - see the [LICENSE](LICENSE) file for details.

---

Made with ❤️ for the Home Assistant and 3D printing community
