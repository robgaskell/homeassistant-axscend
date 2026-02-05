<p style="text-align:center">
    <img alt="Axscend Portal" style="max-width:500px" src="https://portal.axscend.com/images/axscend_blue_logo.svg"/>
</p>

## Axscend Integration for Home Assistant

**Axscend Integration** (`homeassistant_axscend`) is a custom integration for [Home Assistant](https://www.home-assistant.io/) that connects to the [Axscend Portal](https://portal.axscend.com/) telematics platform.  
It lets Home Assistant monitor the location and status of an Axscend asset (for example, a trailer) using the Axscend cloud API.

> **Note**: This is an unofficial community integration and is not affiliated with or endorsed by Axscend Ltd.

---

## Features

- **Single-asset tracking**
  - Monitors a single Axscend asset identified by its Axscend Asset ID.
  - Uses the Axscend v3 API (`https://api.axscend.com/v3`).

- **Sensors**
  - **Asset Name** (`sensor.axscend_asset_name`)
  - **Latitude** (`sensor.axscend_latitude`)
  - **Longitude** (`sensor.axscend_longitude`)
  - **Last Movement** timestamp (`sensor.axscend_last_movement`)
  - **Last Position** timestamp (`sensor.axscend_last_position`)
  - **Battery Level** (`sensor.axscend_battery_level`, %)

- **Binary sensors**
  - **At Home** (`binary_sensor.axscend_at_home`)
    - Uses Home Assistant's configured home location and radius.
    - Calculates distance via Haversine formula.
    - Reports **on** when the asset is within the configured home location radius.

- **Home Assistant native experience**
  - Uses a `DataUpdateCoordinator` for efficient polling.
  - Configured entirely via the UI (Config Flow).
  - Attribution: **Data provided by Axscend**.

---

## Requirements

- A running instance of **Home Assistant** (Core, OS, or Container).  
  - Minimum version (from `hacs.json`): **2025.2.4**.
- **HACS 2.0.5+** if installing via HACS.
- An active **Axscend** account with:
  - An **API token** with access to the asset you want to track.
  - The **Asset ID** of the asset in the Axscend Portal.

You obtain the API token and Asset ID from your Axscend environment (for example by contacting your Axscend administrator or support if they are not visible in the portal UI).

---

## Installation

### Install via HACS (recommended)

1. In Home Assistant, open **HACS → Integrations**.
2. If the integration is **available in the default store**:
   - Search for **“Axscend Integration”** and install it.
3. If it is **not yet in the default store**:
   - Go to **HACS → Integrations → ⋮ → Custom repositories**.
   - Add repository: `https://github.com/robgaskell/homeassistant-axscend`  
     Category: **Integration**.
   - Save, then search for **“Axscend Integration”** in HACS and install it.
4. Restart Home Assistant when prompted.

### Manual installation

1. Browse to your Home Assistant config directory (where `configuration.yaml` lives).
2. Copy the `custom_components/axscend` directory from this repository into your Home Assistant config directory so that you end up with:
   - `config/custom_components/axscend/__init__.py`
   - `config/custom_components/axscend/api.py`
   - `config/custom_components/axscend/*` (all files)
3. Restart Home Assistant.

---

## Configuration

Configuration is done entirely from the Home Assistant UI.

1. In Home Assistant, go to **Settings → Devices & services**.
2. Click **“+ Add integration”**.
3. Search for **“Axscend”** and select **Axscend Integration**.
4. Enter:
   - **API token** – your Axscend API bearer token.
   - **Asset ID** – the Axscend Asset ID you want to track.
5. Click **Submit**.

The integration will:

- Validate your token and Asset ID by making a live call to the Axscend API.
- Fetch the asset’s name so the created config entry title looks like  
  `Axscend Asset 'My Trailer' (123456)`.
- Abort if that Asset ID is already configured in Home Assistant.

If credentials are invalid or the Axscend API cannot be reached, the config flow will show an appropriate error and let you try again.

---

## Exposed entities

Once configured, the integration provides the following entities for the configured asset (entity IDs may vary slightly depending on your setup and language):

- **Sensors**
  - **Asset Name**
    - Type: `sensor`
    - Icon: `mdi:tag`
  - **Latitude**
    - Type: `sensor`
    - Icon: `mdi:latitude`
  - **Longitude**
    - Type: `sensor`
    - Icon: `mdi:longitude`
  - **Last Movement**
    - Type: `sensor`
    - Device class: `timestamp`
    - Description: Last time Axscend reported movement for the asset.
  - **Last Position**
    - Type: `sensor`
    - Device class: `timestamp`
    - Description: Last time Axscend reported a GPS position for the asset.
  - **Battery Level**
    - Type: `sensor`
    - Device class: `battery`
    - Unit: `%`
    - State class: `measurement`
    - Description: Asset device battery level as reported by Axscend.

- **Binary sensor**
  - **At Home**
    - Type: `binary_sensor`
    - Device class: `presence`
    - **on** when the asset is within the configured Home Assistant home location radius.
    - **off** otherwise or when coordinates are unavailable.
    - Uses the radius configured in **Settings → System → General → Home** (defaults to 100 m if not set).

All entities belong to a device named `Axscend Asset <asset_id>` so you can easily find and manage them on the **Devices & services** page.

---

## How it works

- The integration uses an internal **API client** to call the API with your bearer token.
- A **DataUpdateCoordinator** performs periodic polling and shares the latest asset payload with all entities.
- The **binary_sensor** computes distance between the asset coordinates and the Home Assistant home location using the Haversine formula and uses the configured home location radius (defaults to 100 m if not set).

---

## Troubleshooting

- **Authentication errors**
  - Symptoms: Setup flow shows an “authentication” error, or the config entry repeatedly goes into a “reconfigure” state.
  - Check that:
    - The API token is correct and has not expired or been revoked.
    - The Asset ID exists and is accessible with that token.

- **Connection errors**
  - Symptoms: Setup flow or logs show “Unable to connect to the server” or similar.
  - Check:
    - Your Home Assistant host has internet connectivity.
    - There are no firewalls/proxies blocking outbound connections to `https://api.axscend.com`.

- **No location or presence**
  - Ensure:
    - The asset has a current GPS position in Axscend.
    - Home Assistant has a valid home latitude/longitude configured under **Settings → System → General → Home**.

If you run into issues that look like a bug in the integration itself, please open an issue on the GitHub issue tracker:  
`https://github.com/robgaskell/homeassistant-axscend/issues`

---

## Development

This repository includes a development environment and helper scripts:

- **Dev container**: `.devcontainer.json` for running Home Assistant and the integration in a VS Code dev container.
- **Helper scripts** (in `scripts/`):
  - `setup` – prepare the development environment.
  - `develop` – start Home Assistant with this integration mounted for live testing.
  - `lint` – run linters and formatters.

For details on contributing, see `CONTRIBUTING.md`.

---

## License and attribution

- **License**: This project is licensed under the **MIT License**. See `LICENSE` for details.
- **Data attribution**: Data shown by this integration is provided by **Axscend** via the Axscend API.
- **Logo usage**: The Axscend logo and branding are © Axscend Ltd and used here only for identification and documentation purposes, with assets referenced from the official [Axscend Portal](https://portal.axscend.com/).
