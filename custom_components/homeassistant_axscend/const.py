"""Constants for homeassistant_axscend."""

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "homeassistant_axscend"
ATTRIBUTION = "Data provided by Axscend"

API_BASE_URL = "https://api.axscend.com/v3"
API_TIMEOUT = 10  # seconds
API_USER_AGENT = "HomeAssistantAxscendIntegration/1.0"