# options_flow.py
from homeassistant import config_entries
from homeassistant.core import callback
import voluptuous as vol

from .const import CONF_LANGUAGE, CONF_MONTHS, CONF_STRIP_PARENTHESES

# Dictionnaire des langues disponibles (clé = code langue, valeur = label visible)
LANGUAGE_OPTIONS = {
    "en": "English",
    "fr": "Français",
}

# Class gérant les options après l'installation
class DailyTextOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle a config options flow for DailyText."""

    def __init__(self, config_entry):
        """Store config entry for options."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        # Valeurs actuelles (depuis les options, ou les données de config d’origine si options absentes)
        current_language = self.config_entry.options.get(CONF_LANGUAGE, self.config_entry.data.get(CONF_LANGUAGE, "en"))
        current_months = self.config_entry.options.get(CONF_MONTHS, self.config_entry.data.get(CONF_MONTHS, 1))
        current_strip = self.config_entry.options.get(CONF_STRIP_PARENTHESES, self.config_entry.data.get(CONF_STRIP_PARENTHESES, True))

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required(CONF_STRIP_PARENTHESES, description={"translation_key": CONF_STRIP_PARENTHESES}, default=current_strip): bool,
                vol.Required(CONF_MONTHS, description={"translation_key": CONF_MONTHS}, default=current_months): vol.All(vol.Coerce(int), vol.Range(min=1, max=4)),
                vol.Required(CONF_LANGUAGE, description={"translation_key": CONF_LANGUAGE}, default=current_language): vol.In(LANGUAGE_OPTIONS),
            })
        )
