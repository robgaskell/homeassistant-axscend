# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

Always use the venv for running tools — invoke via `.venv/bin/ruff`, `.venv/bin/python`, etc. Do not install packages globally.

```bash
# Start the local Home Assistant dev instance
scripts/develop                     # visits http://127.0.0.1:8123 once running

# Lint and auto-fix
scripts/lint                        # runs ruff format + ruff check --fix

# Lint check only (no changes, used in CI)
ruff check custom_components/
ruff format custom_components/ --check
```

There are no automated tests yet. The CI runs `hassfest` (HA integration validator) and HACS validation via GitHub Actions on push/PR.

## Architecture

This is a Home Assistant custom integration for the Axscend asset-tracking platform. It polls the Axscend REST API on a 5-minute interval and exposes asset data as HA entities.

**Domain:** `axscend` (must match the `custom_components/axscend/` folder name and `manifest.json`).

### Data flow

```
config_flow.py  →  __init__.py  →  coordinator.py  →  api.py  →  Axscend API
                                        ↓
                               sensor.py / binary_sensor.py
```

1. `config_flow.py` collects `api_token` and `asset_id` from the user, validates them via a one-shot API call, then creates the config entry.
2. `__init__.py` (`async_setup_entry`) creates a shared `aiohttp.ClientSession` (using `ThreadedResolver` to avoid `aiodns` issues on Python 3.13+), instantiates the `AxscendApiClient` and `AxscendDataUpdateCoordinator`, then forwards setup to each platform.
3. `coordinator.py` calls `client.async_get_asset(asset_id)` on every poll. The full API response is stored as `coordinator.data`.
4. `sensor.py` and `binary_sensor.py` read from `coordinator.data["asset"]` in their `native_value` / `is_on` properties.

### Key design points

- The `aiohttp.ClientSession` is owned by the config entry (stored in `AxscendData.session`) and must be explicitly closed in `async_unload_entry`. If `async_config_entry_first_refresh` raises, the session is closed in the except block before re-raising.
- `AxscendData` (in `data.py`) is the runtime data dataclass attached to `entry.runtime_data`. It holds the client, coordinator, asset ID, and session.
- Entity unique IDs are formatted as `{entry_id}_{asset_id}_{sensor_key}`. The config entry unique ID is the `asset_id` itself (stable platform identifier).
- The `at_home` binary sensor calculates distance using the Haversine formula against `hass.config.latitude/longitude` with a 100 m threshold.
- `AxscendEntity` (in `entity.py`) is the shared base class for all entities. It sets `DeviceInfo` so all sensors appear under a single device per asset.

### API response shape

The API returns a JSON object with a top-level `"asset"` key:

```json
{
  "asset": {
    "name": "...",
    "gps_latitude": 51.5,
    "gps_longitude": -0.1,
    "last_movement_timestamp": "2026-01-29 21:23:24",
    "last_position_timestamp": "2026-01-29 21:23:24",
    "batt_percent": 85
  }
}
```

Timestamps from the API are in `"YYYY-MM-DD HH:MM:SS"` format and are treated as UTC.
