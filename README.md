# Axscend Integration for Home Assistant

A Home Assistant custom integration for [Axscend](https://axscend.com) asset tracking. It polls the Axscend API every 5 minutes and exposes your asset's location and status as Home Assistant entities.

## Features

- GPS latitude and longitude sensors
- Last movement and last position timestamps
- Battery level sensor
- At Home presence detection (binary sensor based on your HA home location)
- Asset name sensor

## Installation

### HACS (recommended)

1. Open HACS in your Home Assistant instance.
2. Go to **Integrations** → **Custom repositories**.
3. Add `https://github.com/robgaskell/homeassistant_axscend` as an **Integration**.
4. Search for **Axscend** and install it.
5. Restart Home Assistant.

### Manual

1. Copy the `custom_components/axscend` folder into your Home Assistant `custom_components` directory.
2. Restart Home Assistant.

## Configuration

1. Go to **Settings** → **Devices & Services** → **Add Integration**.
2. Search for **Axscend**.
3. Enter your **API Token** and the **Asset ID** you want to track.

The integration will validate your credentials and create a device for the asset.

## Entities

Each configured asset creates the following entities:

| Entity | Type | Description |
|--------|------|-------------|
| Asset Name | Sensor | The name of the asset as set in Axscend |
| Latitude | Sensor | Current GPS latitude |
| Longitude | Sensor | Current GPS longitude |
| Last Movement | Sensor | Timestamp of the asset's last detected movement |
| Last Position | Sensor | Timestamp of the last GPS position fix |
| Battery Level | Sensor | Tracker battery percentage |
| At Home | Binary Sensor | `on` when the asset is within 100 m of your HA home location |

## Requirements

- Home Assistant 2025.2 or newer
- An [Axscend](https://portal.axscend.com) account with an API token
- The Asset ID of the tracker you want to monitor

## Development

### Dev container (recommended)

The repository includes a VS Code dev container that spins up a Python 3.13 environment with all dependencies pre-installed and port 8123 forwarded for a local Home Assistant instance.

1. Open the repository in VS Code.
2. When prompted, click **Reopen in Container** (or run **Dev Containers: Reopen in Container** from the command palette).
3. The container runs `scripts/setup` on creation, which installs everything from `requirements.txt`.

To test the integration against a running Home Assistant instance, copy (or symlink) the `custom_components/axscend` folder into your HA `config/custom_components/` directory and restart HA.

### Local setup (without dev container)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Linting

```bash
scripts/lint          # auto-formats and fixes lint errors
```

To check only (as CI does):

```bash
ruff check custom_components/
ruff format custom_components/ --check
```
