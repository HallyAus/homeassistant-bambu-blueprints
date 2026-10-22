## GitHub source control and self-hosted runner (current policy, 2026-10-22)

- **Canonical repository:** `https://github.com/HallyAus/homeassistant-bambu-blueprints`. GitHub is the source of truth. Commit, push, open pull requests and publish tags/releases to GitHub; do not publish to former Git servers or maintain a secondary recovery mirror.
- **Branch and remote:** Use the repository's current GitHub default/production branch, verify `git remote -v` before pushing, preserve uncommitted work and never force-push over newer commits.
- **CI/CD:** A self-hosted GitHub Actions runner is available. Prefer it for eligible jobs when the repository has a configured workflow; use the exact runner labels verified in repository settings or existing workflows. Do not assume the runner's OS, permissions, online status or available secrets, and do not expose credentials to untrusted contributions.
- **Validation and deployment:** Keep the project's existing tests, security checks, branch protections, release approvals, staging/acceptance and production verification. A GitHub push or green build is not proof of production deployment. Do not silently enable or bypass deployment triggers, and never infer that Vercel, Proxmox or another target deploys automatically.
- **Precedence:** This section overrides older hosting, mirror, disabled-Actions and publishing instructions elsewhere in this file. Preserve non-hosting project-specific safety rules.

# Personal source and validation
