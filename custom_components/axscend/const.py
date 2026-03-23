"""Constants for axscend."""

import json
from logging import Logger, getLogger
from pathlib import Path

LOGGER: Logger = getLogger(__package__)

DOMAIN = "axscend"
ATTRIBUTION = "Data provided by Axscend"

# Config flow constants
CONF_ASSET_ID = "asset_id"

API_BASE_URL = "https://api.axscend.com/v3"
API_TIMEOUT = 10  # seconds

_manifest = json.loads((Path(__file__).parent / "manifest.json").read_text())
API_USER_AGENT = f"HomeAssistantAxscendIntegration/{_manifest['version']}"
