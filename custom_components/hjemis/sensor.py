import logging
from datetime import datetime

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from .const import DOMAIN

async def async_setup_entry(hass, config_entry, async_add_entries):
    """Set up the sensor platform for HjemIS"""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entries([HjemISSensor(coordinator)], True)

class HjemISSensor(SensorEntity):
    """Representation of a sensor for the next HjemIS visit."""

    def __init__(self, coordinator):
        """Initialise the sensor."""
        self.coordinator = coordinator
        self._attr_name = "Next HjemIS visit"
        self._attr_unique_id = "hjemis_next_visit"
        self._attr_icon = "mdi:ice-cream"
        self._attr_device_class = SensorDeviceClass.TIMESTAMP

    async def async_added_to_hass(self):
        """When entity is added to hass."""
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )

    @property
    def available(self):
        """Return if entity is available."""
        return self.coordinator.last_update_success

    @property
    def state(self):
        """Return the raw timestamp as the state."""
        data = self.coordinator.data
        if data and isinstance(data, list) and len(data) > 0:
            next_event = data[0]
            return next_event.get("google_estimate_time", None)
        return None

    @property
    def extra_state_attributes(self):
        """Return additional attributes."""
        data = self.coordinator.data
        if data and isinstance(data, list) and len(data) > 0:
            next_event = data[0]
            return {
                "address": next_event.get("address", "unknown"),
                "distance": next_event.get("distance", "unknown")
            }
        return {}