import voluptuous as vol
import homeassistant.helpers.config_validation as cv

from homeassistant import config_entries
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE

from .const import DOMAIN

# This class handles the initial configuration of the integration.
class HjemISConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for the HjemIS integration."""
    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step where the user enters their home coordinates."""
        if user_input is None:
            # Pre-fill the form using Home Assistant's configured home location.
            default_lat = self.hass.config.latitude
            default_lon = self.hass.config.longitude

            data_schema = vol.Schema({
                vol.Required(CONF_LATITUDE, default=default_lat): cv.latitude,
                vol.Required(CONF_LONGITUDE, default=default_lon): cv.longitude,
            })
            return self.async_show_form(step_id="user", data_schema=data_schema)

        # Create the entry once the user has provided their input.
        return self.async_create_entry(title="HjemIS", data=user_input)

    @staticmethod
    def async_get_options_flow(config_entry):
        """Return the options flow."""
        return HjemISOptionsFlowHandler(config_entry)


# This class provides a minimal options flow.
class HjemISOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options for the HjemIS integration."""

    def __init__(self, config_entry):
        """Initialize the options flow."""
        self._entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        # For now, we don't have any options so simply finish.
        # If you want to add options later, you can define a form here.
        return self.async_create_entry(title="", data=user_input or {})
