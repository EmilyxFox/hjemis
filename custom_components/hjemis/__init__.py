import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DOMAIN
from .coordinator import HjemISDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the HjemIS integration from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    coordinator = HjemISDataUpdateCoordinator(
        hass,
        entry.data[CONF_LATITUDE],
        entry.data[CONF_LONGITUDE],
    )

    try:
        # Perform the first data refresh. If it fails, raise ConfigEntryNotReady.
        await coordinator.async_config_entry_first_refresh()
    except Exception as err:
        _LOGGER.error("Error fetching initial data: %s", err)
        raise ConfigEntryNotReady from err
    
    # Store the coordinator so that platforms can access it.
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Forward setup to sensor platform.
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor"])
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok