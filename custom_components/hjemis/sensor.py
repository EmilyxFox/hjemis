from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from .const import DOMAIN

async def async_setup_entry(hass, config_entry, async_add_entries):
    """Set up the sensor platform for HjemIS"""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entries([HjemISSensor(coordinator, config_entry.entry_id)], True)

class HjemISSensor(SensorEntity):
    """Representation of a sensor for the next HjemIS visit."""

    def __init__(self, coordinator, config_entry_id):
        """Initialise the sensor."""
        self.coordinator = coordinator
        self._entry_id = config_entry_id
        self._attr_icon = "mdi:ice-cream"
        self._attr_device_class = SensorDeviceClass.TIMESTAMP

    async def async_added_to_hass(self):
        """When entity is added to hass."""
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )

        await self._update_name()

    async def _update_name(self):
        """Update the sensor name based on the country."""
        if self.coordinator.data and "country" in self.coordinator.data:
            country = self.coordinator.data["country"]
            if country == "Norway":
                self._attr_name = "Next Fråst visit"
                self._attr_unique_id = f"frost_next_visit_{self._entry_id}"
            else:
                self._attr_name = "Next HjemIS visit"
                self._attr_unique_id = f"hjemis_next_visit_{self._entry_id}"
        else:
            # Default name until we know the country
            self._attr_name = "Next ice cream visit"
            self._attr_unique_id = f"icecream_next_visit_{self._entry_id}"

    @property
    def available(self):
        """Return if entity is available."""
        return self.coordinator.last_update_success

    @property
    def state(self):
        """Return the raw timestamp as the state."""
        if not self.coordinator.data or "data" not in self.coordinator.data:
            return None
            
        data = self.coordinator.data["data"]
        if data and isinstance(data, list) and len(data) > 0:
            next_event = data[0]
            return next_event.get("google_estimate_time", None)
        return None

    @property
    def extra_state_attributes(self):
        """Return additional attributes."""
        if not self.coordinator.data or "data" not in self.coordinator.data:
            return {}
            
        data = self.coordinator.data["data"]
        country = self.coordinator.data.get("country", "unknown")
        
        if data and isinstance(data, list) and len(data) > 0:
            next_event = data[0]
            return {
                "address": next_event.get("address", "unknown"),
                "distance": next_event.get("distance", "unknown"),
                "country": country,
                "brand": "Fråst" if country == "Norway" else "HjemIS"
            }
        return {"country": country, "brand": "Fråst" if country == "Norway" else "HjemIS"}