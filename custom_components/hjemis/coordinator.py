import logging
import aiohttp
from datetime import timedelta

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

_LOGGER = logging.getLogger(__name__)

API_URL = "https://sms.hjem-is.dk/dk.json"

async def async_fetch_data(session, lat, lon):
    """Fetch data from the external API using provided coordinates."""
    _LOGGER.debug("Fetching data from HjemIS API with coordinates: lat=%s, lon=%s", lat, lon)
    params = {"coordinates[lat]": lat, "coordinates[lng]": lon}
    async with session.get(API_URL, params=params) as response:
        if response.status != 200:
            _LOGGER.error("Error fetching data: %s", response.status)
            raise UpdateFailed(f"Error fetching data: {response.status}")
        json = await response.json()
        return json

class HjemISDataUpdateCoordinator(DataUpdateCoordinator):
    """Coordinator to fetch data from the HjemIS API."""

    def __init__(self, hass, lat, lon):
        """Initialize the coordinator."""
        self.lat = lat
        self.lon = lon
        _LOGGER.debug("Initializing HjemIS coordinator with lat=%s, lon=%s", lat, lon)
        super().__init__(
            hass,
            _LOGGER,
            name="HjemIS Data Collector",
            update_interval=timedelta(hours=1),
        )

    async def _async_update_data(self):
        """Fetch data from the API."""
        _LOGGER.debug("Running update for HjemIS coordinator")
        try:
            async with aiohttp.ClientSession() as session:
                data = await async_fetch_data(session, self.lat, self.lon)
                _LOGGER.debug("HjemIS update successful, data length: %s", len(data) if isinstance(data, list) else "not a list")
                return data
        except Exception as err:
            _LOGGER.exception("Unexpected error occurred during HjemIS update: %s", err)
            raise UpdateFailed(f"Error updating HjemIS data: {err}")