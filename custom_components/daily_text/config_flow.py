# config_flow.py
from homeassistant import config_entries
from homeassistant.core import callback
import voluptuous as vol
from .const import DOMAIN, CONF_LANGUAGE, CONF_MONTHS, CONF_STRIP_PARENTHESES, DEFAULT_STRIP_PARENTHESES
from .options_flow import DailyTextOptionsFlowHandler

LANGUAGES = {
    "en": "English",
    "fr": "Français",
}

# Class gérant l'installation
class DailyTextConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="Daily Text", data=user_input)

        step_id="user",
        schema = vol.Schema({
            vol.Required(CONF_STRIP_PARENTHESES, description={"translation_key": CONF_STRIP_PARENTHESES}, default=DEFAULT_STRIP_PARENTHESES): bool,
            vol.Required(CONF_MONTHS, description={"translation_key": CONF_MONTHS}, default=1): vol.All(vol.Coerce(int), vol.Range(min=1, max=4)),
            vol.Required(CONF_LANGUAGE, description={"translation_key": CONF_LANGUAGE}, default="en"): vol.In(LANGUAGES),
        })

        return self.async_show_form(step_id="user", data_schema=schema)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return DailyTextOptionsFlowHandler(config_entry)
