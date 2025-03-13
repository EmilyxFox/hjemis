import logging
import aiohttp
from datetime import timedelta

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from .const import API_URL_DK, API_URL_NO

_LOGGER = logging.getLogger(__name__)

def is_in_norway(lat, lon):
    """Determine if coordinates are in Norway.
    
    This check seems really stupid, but its sufficient for now.
    The function still takes in both just in case the check needs to be
    complicated in the future.
    """
    return lat > 57.9

async def async_fetch_data(session, lat, lon):
    """Fetch data from the external API using provided coordinates."""
    if is_in_norway(lat, lon):
        api_url = API_URL_NO
        country = "Norway"
    else:
        api_url = API_URL_DK
        country = "Denmark"
        
    _LOGGER.debug("Fetching data from API (%s) with coordinates: lat=%s, lon=%s", country, lat, lon)
    params = {"coordinates[lat]": lat, "coordinates[lng]": lon}
    async with session.get(api_url, params=params) as response:
        if response.status != 200:
            _LOGGER.error("Error fetching data: %s", response.status)
            raise UpdateFailed(f"Error fetching data: {response.status}")
        json = await response.json()
        return {"data": json, "country": country}

class HjemISDataUpdateCoordinator(DataUpdateCoordinator):
    """Coordinator to fetch data from the HjemIS API."""

    def __init__(self, hass, lat, lon):
        """Initialize the coordinator."""
        self.lat = lat
        self.lon = lon
        _LOGGER.debug("Initializing coordinator with lat=%s, lon=%s", lat, lon)
        super().__init__(
            hass,
            _LOGGER,
            name="HjemIS/Fråst Data Collector",
            update_interval=timedelta(hours=1),
        )

    async def _async_update_data(self):
        """Fetch data from the API."""
        _LOGGER.debug("Running update for coordinator")
        try:
            async with aiohttp.ClientSession() as session:
                result = await async_fetch_data(session, self.lat, self.lon)
                data = result["data"]
                country = result["country"]
                _LOGGER.debug("Update successful for %s, data length: %s", 
                             country, 
                             len(data) if isinstance(data, list) else "not a list")
                return {"data": data, "country": country}
        except Exception as err:
            _LOGGER.exception("Unexpected error occurred during update: %s", err)
            raise UpdateFailed(f"Error updating data: {err}")