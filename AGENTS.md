## Canonical GitHub source and self-hosted Actions (2026-10-22)

GitHub `https://github.com/HallyAus/homeassistant-bambu-blueprints` is authoritative for source, commits and releases. Push to the verified GitHub remote and current project branch, not any retired internal forge or recovery mirror. Preserve local work and never force push. Use the configured self-hosted GitHub Actions runner where available, checking actual job labels, runner trust and workflow configuration. Keep existing release gates, production settings, credentials boundaries, rollback, stage/promotion and live validation. Neither a push nor green CI alone proves deployment. Historical source-control instructions below are superseded.

# Personal source and validation

GitHub is the primary source. Preserve existing public blueprint import URLs until any replacement is verified for installed users.

GitHub Actions validation must retain the two real Home Assistant test environments: Python3.12/HA2024.6.0 and Python3.14/HA2026.9.3. Use the configured personal self-hosted runner. Tests use synthetic entities and mocked services; never send real notifications, capture a real camera, call a printer or reload/restart Home Assistant as a test. Both distributed blueprint YAML copies must remain byte-identical.

Do not revive the historical PR11 comment-triggered patch workflow. It writes branches and is unrelated to current validation. A private candidate artifact is not an installed release. Keep M4T, Kidde and Proxmox.99 outside this work.
