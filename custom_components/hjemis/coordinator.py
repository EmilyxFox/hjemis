import logging
import json # For json.JSONDecodeError
import aiohttp
from datetime import timedelta

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from .const import API_URL_DK, API_URL_NO # Assuming these are defined in your const.py

_LOGGER = logging.getLogger(__name__)

INTEGRATION_VERSION = "0.2.1" # Or dynamically get this if possible
USER_AGENT_STRING = f"HomeAssistant-HjemIS&Fråst/{INTEGRATION_VERSION} (+https://github.com/EmilyxFox/hjemis)"

def is_in_norway(lat, lon):
    """Determine if coordinates are in Norway."""
    return lat > 57.9

async def async_fetch_data(session: aiohttp.ClientSession, lat: float, lon: float):
    """Fetch data from the external API using provided coordinates."""
    if is_in_norway(lat, lon):
        api_url = API_URL_NO
        country = "Norway"
    else:
        api_url = API_URL_DK
        country = "Denmark"
            
    _LOGGER.debug("Fetching data for %s from API URL: %s with coordinates: lat=%s, lon=%s", country, api_url, lat, lon)
    params = {"coordinates[lat]": lat, "coordinates[lng]": lon, "format": "json"}

    try:
        async with session.get(api_url, params=params) as response:
            _LOGGER.debug("Request URL: %s", response.url)
            _LOGGER.debug("Response status: %s", response.status)
            _LOGGER.debug("Response headers: %s", response.headers)
            
            response_text = await response.text() # Log raw text first for debugging
            _LOGGER.debug("Raw API Response text: %s", response_text)

            if response.status != 200:
                _LOGGER.error("Error fetching data: HTTP %s - %s", response.status, response_text[:200]) # Log snippet of error
                raise UpdateFailed(f"Error fetching data: HTTP {response.status}")

            # Handle cases where API might return an empty string or the literal string "null"
            # For this API, an empty list "[]" is valid for "no data points".
            if not response_text: # Empty string response
                _LOGGER.warning("API returned an empty response body for %s (lat:%s, lon:%s). Treating as no data (empty list).", country, lat, lon)
                return {"data": [], "country": country} # Return empty list to match expected data type
            
            if response_text.lower() == "null": # Literal "null" string response (less likely if API returns [] for no data)
                _LOGGER.warning("API returned 'null' string response body for %s (lat:%s, lon:%s). Treating as no data (empty list).", country, lat, lon)
                return {"data": [], "country": country} # Return empty list

            # Attempt to parse JSON using aiohttp's built-in method
            try:
                json_data = await response.json(content_type=None) # content_type=None makes it more flexible
            except (aiohttp.client_exceptions.ContentTypeError, json.JSONDecodeError) as parse_err: # Catch specific parsing errors
                _LOGGER.error("Failed to parse JSON response for %s (lat:%s, lon:%s): %s", country, lat, lon, parse_err)
                # response_text is already logged above.
                raise UpdateFailed(f"Failed to parse JSON response: {parse_err}")

            # Validate if the parsed data is a list, as per the example response
            if not isinstance(json_data, list):
                _LOGGER.error("API response parsed successfully but is not a JSON list as expected. Type: %s", type(json_data))
                _LOGGER.debug("Unexpected data structure (first 200 chars): %s", str(json_data)[:200])
                # This could be an API error object like {"error": "message"} that is valid JSON but not a list.
                # Depending on API, you might want to inspect this further or extract an error message.
                # For now, if it's not a list, this integration cannot process it as expected.
                raise UpdateFailed(f"API response is not in the expected list format: received type {type(json_data)}")
                
            _LOGGER.debug("Successfully parsed JSON response. Data is a list of %d items.", len(json_data))
            return {"data": json_data, "country": country} # json_data will be [] if API returned an empty list

    except aiohttp.ClientError as err: # Network-related errors
        _LOGGER.error("Network or client error fetching data for %s: %s", country, err)
        raise UpdateFailed(f"Network error for {country}: {err}")
    # UpdateFailed exceptions from within the try block will propagate up
    # Catch any other truly unexpected exceptions:
    except Exception as err: 
        _LOGGER.exception("Unexpected error during data fetch for %s (lat:%s, lon:%s). This may be a bug in the integration.", country, lat, lon)
        raise UpdateFailed(f"Unexpected error processing data for {country}: {err}")


class HjemISDataUpdateCoordinator(DataUpdateCoordinator):
    """Coordinator to fetch data from the HjemIS API."""

    def __init__(self, hass, lat, lon):
        """Initialize the coordinator."""
        self.lat = lat
        self.lon = lon
        _LOGGER.debug("Initializing HjemISDataUpdateCoordinator with lat=%s, lon=%s", lat, lon)
        super().__init__(
            hass,
            _LOGGER,
            name="HjemIS/Fråst Data Collector",
            update_interval=timedelta(hours=1),
        )

    async def _async_update_data(self):
        """Fetch data from the API."""
        _LOGGER.debug("HjemISDataUpdateCoordinator: Starting data update run.")
        try:
            headers = {
                "Accept": "application/json",
                "User-Agent": USER_AGENT_STRING
            }
            _LOGGER.debug("Using headers for API request: %s", headers)

            async with aiohttp.ClientSession(headers=headers) as session:
                result = await async_fetch_data(session, self.lat, self.lon)
                
                data = result.get("data") 
                country = result.get("country")

                # Data should now always be a list (possibly empty) if async_fetch_data was successful
                item_count = "unknown"
                if isinstance(data, list):
                    item_count = len(data)
                
                _LOGGER.debug(
                    "Update successful for %s. Received %s items. Data snippet: %s", 
                    country,
                    item_count,
                    str(data)[:300] + ("..." if len(str(data)) > 300 else "") # Log a snippet
                )
                return {"data": data, "country": country}
        except UpdateFailed as e:
            _LOGGER.warning("UpdateFailed caught in HjemISDataUpdateCoordinator: %s", e) # Log as warning, coordinator handles it
            raise
        except Exception as err:
            _LOGGER.exception("Unexpected error occurred during HjemIS data update: %s", err)
            raise UpdateFailed(f"Unforeseen error updating HjemIS data: {err}")