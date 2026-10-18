# Personal source and validation

Use private VM300 `hallyaus/homeassistant-bambu-blueprints` as origin, Git SSH2222.
Push completed, validated source there first and then the identical GitHub
recovery commit. Keep GitHub Actions disabled and preserve existing public
blueprint import URLs until a replacement has been verified for installed users.

Gitea validation retains both original real Home Assistant test environments:
Python3.12/HA2024.6.0 and Python3.14/HA2026.9.3. Use only the personal runner.
Tests use synthetic entities and mocked services; never send real notifications,
capture a real camera, call a printer or reload/restart Home Assistant as a test.
Both distributed blueprint YAML copies must remain byte-identical.

Do not revive the historical PR11 comment-triggered patch workflow. It writes
branches and is unrelated to current validation. Preserve its history with
GitHub Actions disabled. A private candidate artifact is not an installed release.
Keep M4T, Kidde and Proxmox.99 outside this work.
