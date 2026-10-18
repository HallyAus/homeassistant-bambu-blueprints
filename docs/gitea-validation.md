# Personal validation migration

Gitea is the private primary source. The new workflow preserves the existing
two real automation-engine test environments and its complete pytest suite.
The test service registrations are mocked and use synthetic entities; no real
printer, camera, mobile notification, TTS device or installed HA instance is
called. Blueprint behavior and both published YAML copies remain unchanged.

The first complete Linux matrix must pass before recovery is updated. GitHub
Actions remain disabled. Installed import/update links still use the existing
public GitHub raw YAML as a compatibility consumer, with identical completed
source pushed only after VM300 validation. This is not a new public Gitea route
or a claim that a Home Assistant installation was updated.

The historical PR11 comment patch is not migrated or executed: current main
already contains the later notification reliability fixes. Preserve its source
history without enabling GitHub execution. No periodic schedule existed in the
original blueprint validation workflow.
