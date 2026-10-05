"""Exercise the imported blueprint with Home Assistant's real automation engine."""

import asyncio
import inspect
from datetime import datetime
from pathlib import Path
from unittest.mock import AsyncMock

import pytest
import yaml
from homeassistant.core import CoreState, HomeAssistant
from homeassistant import config_entries, loader
from homeassistant.components.blueprint.models import Blueprint, BlueprintInputs
from homeassistant.components.blueprint.schemas import BLUEPRINT_SCHEMA
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import area_registry, condition, device_registry, entity_registry, storage, trigger
from homeassistant.helpers.template import Template
from homeassistant.setup import async_setup_component
from homeassistant.util.yaml import load_yaml

ROOT = Path(__file__).resolve().parents[1]
COPIES = [ROOT / "bambu_print_notify.yaml", ROOT / "blueprints/automation/danielhall/bambu_print_notify.yaml"]
INPUTS = {
    "print_status_sensor": "sensor.printer_status",
    "print_error_binary": "binary_sensor.printer_error",
    "current_stage_sensor": "sensor.printer_stage",
    "progress_sensor": "sensor.printer_progress",
    "printer_name_sensor": "sensor.printer_name",
    "task_name_sensor": "sensor.printer_task",
    "print_weight_sensor": "sensor.printer_weight",
    "camera": "camera.printer",
    "notifications_enabled_boolean": "input_boolean.notifications",
    "snapshot_delay_seconds": 0,
    "notify_device": "mobile_app_phone",
    "cooldown_minutes": 0,
}


def load_blueprint(path):
    # New HA versions require callers to supply the blueprint schema explicitly.
    kwargs = {"schema": BLUEPRINT_SCHEMA} if "schema" in inspect.signature(Blueprint).parameters else {}
    return Blueprint(load_yaml(str(path)), expected_domain="automation", **kwargs)


def expand(**overrides):
    blueprint = load_blueprint(COPIES[0])
    inputs = BlueprintInputs(blueprint, {
        "id": "bambu_test",
        "alias": "Bambu test",
        "use_blueprint": {"path": "test.yaml", "input": INPUTS | overrides},
    })
    inputs.validate()
    return inputs.async_substitute()


def test_copies_match_and_blueprint_schema_is_valid():
    assert COPIES[0].read_bytes() == COPIES[1].read_bytes()
    for path in COPIES:
        blueprint = load_blueprint(path)
        assert blueprint.validate() is None


def test_yaml_has_no_duplicate_keys():
    class UniqueLoader(yaml.SafeLoader):
        def construct_mapping(self, node, deep=False):
            keys = [key.value for key, _ in node.value]
            assert len(keys) == len(set(keys)), f"Duplicate key at {node.start_mark}"
            return super().construct_mapping(node, deep)

    UniqueLoader.add_constructor("!input", lambda loader, node: loader.construct_scalar(node))
    for path in [*COPIES, *ROOT.glob(".github/workflows/*.yml")]:
        yaml.load(path.read_text(encoding="utf-8"), Loader=UniqueLoader)


@pytest.fixture
async def runtime(tmp_path, monkeypatch):
    # Tests use synthetic entities and never persist state or control hardware.
    monkeypatch.setattr(storage.Store, "_async_write_data", AsyncMock())
    hass = HomeAssistant(str(tmp_path))
    loader.async_setup(hass)
    for helper in (trigger, condition):
        if hasattr(helper, "async_setup"):
            await helper.async_setup(hass)
    hass.config_entries = config_entries.ConfigEntries(hass, {})
    await hass.config_entries.async_initialize()
    for registry in (area_registry, device_registry, entity_registry):
        if hasattr(registry, "async_setup"):
            registry.async_setup(hass)
        if hasattr(registry, "async_load"):
            await registry.async_load(hass)
        else:
            await registry.async_get(hass).async_load()
    hass.state = CoreState.running
    calls = []
    snapshot = asyncio.Event()
    delivered = asyncio.Event()
    snapshot_hook = None
    failing = set()

    async def record(call):
        calls.append(call)
        if call.domain == "camera":
            snapshot.set()
            if snapshot_hook:
                await snapshot_hook()
        if (call.domain, call.service) in failing:
            raise HomeAssistantError("Simulated optional service failure")
        if call.domain == "notify":
            delivered.set()

    for domain, service in [
        ("camera", "snapshot"), ("notify", "mobile_app_phone"),
        ("notify", "send_message"), ("tts", "speak"),
        ("tts", "legacy_say"), ("media_player", "volume_set"),
        ("light", "turn_on"), ("light", "turn_off"),
        ("persistent_notification", "create"),
        ("test", "success"), ("test", "fault"),
    ]:
        hass.services.async_register(domain, service, record)
    for entity, value in {
        "sensor.printer_status": "running", "binary_sensor.printer_error": "off",
        "sensor.printer_stage": "printing", "sensor.printer_progress": "98",
        "sensor.printer_name": "P1S", "sensor.printer_task": "benchy.3mf",
        "sensor.printer_weight": "15", "input_boolean.notifications": "on",
    }.items():
        hass.states.async_set(entity, value)

    class Runtime:
        async def start(self, hook=None, wait_timeout=None, **inputs):
            nonlocal snapshot_hook
            snapshot_hook = hook
            config = expand(**inputs)
            if wait_timeout is not None:
                for action in config["action"]:
                    for step in action.get("then", []):
                        if "wait_template" in step:
                            step["timeout"] = wait_timeout
            assert await async_setup_component(hass, "automation", {"automation": [config]})
            await hass.async_block_till_done()
            assert hass.states.get("automation.bambu_test").state == "on"

        def set(self, entity, value):
            hass.states.async_set(entity, value)

        def matching(self, domain, service=None):
            return [c for c in calls if c.domain == domain and (service is None or c.service == service)]

        async def finish(self):
            await asyncio.wait_for(delivered.wait(), timeout=5)
            await hass.async_block_till_done()

    runtime = Runtime()
    runtime.hass = hass
    runtime.snapshot = snapshot
    runtime.failing = failing
    yield runtime
    await hass.async_stop(force=True)


@pytest.mark.parametrize("end_state", ["finish", "idle", "failed"])
async def test_completion_during_snapshot_does_not_wait_ten_minutes(runtime, end_state):
    async def complete_during_capture():
        runtime.set("sensor.printer_status", "finish")
        runtime.set("sensor.printer_status", end_state)

    await runtime.start(hook=complete_during_capture)
    runtime.set("sensor.printer_progress", "100")
    await runtime.finish()
    notifications = runtime.matching("notify")
    assert len(notifications) == 1
    assert len(runtime.matching("camera")) == 1
    assert ("FAULT" in notifications[0].data["title"]) == (end_state == "failed")


async def test_waits_for_actual_completion_and_refreshes_message(runtime):
    await runtime.start(progress_trigger_threshold=97)
    runtime.set("sensor.printer_progress", "97")
    await runtime.hass.async_block_till_done()
    runtime.set("sensor.printer_progress", "98")
    await asyncio.wait_for(runtime.snapshot.wait(), 5)
    assert not runtime.matching("notify")
    runtime.set("sensor.printer_progress", "100")
    runtime.set("sensor.printer_status", "finish")
    await runtime.finish()
    assert len(runtime.matching("camera")) == 1
    assert len(runtime.matching("notify")) == 1
    assert "100%" in runtime.matching("notify")[0].data["message"]


@pytest.mark.parametrize("service", ["mobile_app_phone", "notify.mobile_app_phone", "  notify.mobile_app_phone  "])
async def test_legacy_service_retains_rich_payload(runtime, service):
    await runtime.start(notify_device=service, success_notification_type="critical",
                        printers_view_uri='/lovelace/printers?name="P1S"')
    runtime.set("sensor.printer_status", "finish")
    await runtime.finish()
    payload = runtime.matching("notify")[0].data["data"]
    assert payload["push"]["sound"]["critical"] == 1
    assert payload["sticky"] is False
    assert payload["image"].startswith("/local/snapshots/bambu_bambu_test.jpg?v=")
    assert payload["actions"][0]["uri"] == '/lovelace/printers?name="P1S"'


async def test_notify_entities_use_only_supported_fields(runtime):
    await runtime.start(notify_device="", notify_entities=["notify.phone", "notify.tablet"])
    runtime.set("sensor.printer_status", "finish")
    await runtime.finish()
    call, = runtime.matching("notify")
    assert call.service == "send_message"
    assert set(call.data) == {"entity_id", "title", "message"}
    assert call.data["entity_id"] == ["notify.phone", "notify.tablet"]


@pytest.mark.parametrize("service", ["tts.speak", "", "tts.legacy_say"])
async def test_tts_uses_engine_and_renders_message_after_sensor_values(runtime, service):
    await runtime.start(tts_enable=True, tts_service=service, tts_engine="tts.piper",
                        tts_media_player=["media_player.speaker"])
    runtime.set("sensor.printer_status", "finish")
    await runtime.finish()
    call, = runtime.matching("tts")
    assert call.data["message"] == "P1S has finished printing benchy.3mf"
    if service != "tts.legacy_say":
        assert call.data["entity_id"] == ["tts.piper"]
        assert call.data["media_player_entity_id"] == ["media_player.speaker"]


async def test_fault_is_preserved_when_sensor_clears_during_snapshot(runtime):
    async def clear_fault():
        runtime.set("sensor.printer_status", "idle")
        runtime.set("binary_sensor.printer_error", "off")

    await runtime.start(hook=clear_fault, fault_actions=[{"service": "test.fault"}])
    runtime.set("binary_sensor.printer_error", "on")
    await runtime.finish()
    assert "FAULT" in runtime.matching("notify")[0].data["title"]
    assert len(runtime.matching("test", "fault")) == 1


async def test_optional_service_failures_do_not_block_other_channels_or_custom_actions(runtime):
    runtime.failing.update({("notify", "mobile_app_phone"), ("camera", "snapshot"), ("light", "turn_on")})
    await runtime.start(snapshot_light="light.printer", notify_entities=["notify.phone"],
                        success_actions=[{"service": "test.success", "data": {"progress": "{{ progress }}"}}])
    runtime.set("sensor.printer_status", "finish")
    await runtime.finish()
    assert len(runtime.matching("notify", "send_message")) == 1
    assert len(runtime.matching("light", "turn_off")) == 1
    assert len(runtime.matching("test", "success")) == 1


@pytest.mark.parametrize("state", ["pause", "offline", "unknown", "unavailable", "running"])
async def test_unfinished_print_times_out_without_success(runtime, state):
    async def unfinished():
        runtime.set("sensor.printer_status", state)

    await runtime.start(hook=unfinished, wait_timeout={"milliseconds": 1},
                        success_actions=[{"service": "test.success"}])
    runtime.set("sensor.printer_progress", "100")
    await asyncio.wait_for(runtime.hass.async_block_till_done(), 5)
    assert len(runtime.matching("camera")) == 1
    assert not runtime.matching("notify")
    assert not runtime.matching("test")


async def test_cooldown_uses_automation_last_triggered(runtime):
    await runtime.start(cooldown_minutes=5)
    runtime.set("sensor.printer_status", "finish")
    await runtime.finish()
    runtime.set("sensor.printer_status", "running")
    await runtime.hass.async_block_till_done()
    runtime.set("sensor.printer_status", "finish")
    await runtime.hass.async_block_till_done()
    assert len(runtime.matching("notify")) == 1
    assert len(runtime.matching("camera")) == 1


@pytest.mark.parametrize("previous", ["offline", "unavailable", "unknown"])
async def test_reconnect_does_not_notify(runtime, previous):
    runtime.set("sensor.printer_status", previous)
    runtime.set("sensor.printer_progress", "unavailable")
    await runtime.start()
    runtime.set("sensor.printer_status", "finish")
    runtime.set("sensor.printer_progress", "100")
    await runtime.hass.async_block_till_done()
    assert not runtime.matching("camera")
    assert not runtime.matching("notify")


async def test_fault_at_zero_progress_is_not_suppressed(runtime):
    runtime.set("sensor.printer_status", "prepare")
    runtime.set("sensor.printer_progress", "0")
    runtime.set("sensor.printer_stage", "idle")
    await runtime.start()
    runtime.set("sensor.printer_status", "failed")
    await runtime.finish()
    assert "FAULT" in runtime.matching("notify")[0].data["title"]
    assert len(runtime.matching("persistent_notification")) == 1


async def test_disabled_notifications_do_not_run_actions(runtime):
    runtime.set("input_boolean.notifications", "off")
    await runtime.start()
    runtime.set("sensor.printer_status", "finish")
    await runtime.hass.async_block_till_done()
    assert not runtime.matching("camera")
    assert not runtime.matching("notify")


async def test_missing_legacy_service_does_not_block_entity_delivery(runtime):
    await runtime.start(notify_device="missing", notify_entities=["notify.phone"])
    runtime.set("sensor.printer_status", "finish")
    await runtime.finish()
    assert len(runtime.matching("notify", "send_message")) == 1


@pytest.mark.parametrize("hour,expected", [(6, True), (7, False), (12, False), (22, True), (23, True)])
async def test_quiet_hours_cross_midnight(runtime, hour, expected):
    config = expand(tts_quiet_hours_enable=True)
    variables = next(a["variables"] for a in config["action"] if "is_tts_quiet_hours" in a.get("variables", {}))
    template = Template(variables["is_tts_quiet_hours"], runtime.hass)
    assert template.async_render({
        "tts_quiet_hours_enable": True,
        "tts_quiet_hours_start": "22:00:00",
        "tts_quiet_hours_end": "07:00:00",
        "now": lambda: datetime(2026, 9, 19, hour),
    }) is expected
