# sensor.py
from homeassistant.components.sensor import SensorEntity
from .const import DOMAIN, CONF_LANGUAGE, CONF_MONTHS, CONF_STRIP_PARENTHESES
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

async def async_setup_entry(hass, config_entry, async_add_entities):
    sensor = DailyTextConfigSensor(config_entry)
    async_add_entities([sensor], update_before_add=True)

    # Enregistre une fonction de rappel qui sera appelée lors d'une mise à jour
    config_entry.async_on_unload(
        config_entry.add_update_listener(sensor.async_config_entry_updated)
    )

class DailyTextConfigSensor(SensorEntity):
    """Sensor to expose Daily Text configuration options."""

    _attr_has_entity_name = True
    _attr_should_poll = False
    _attr_icon = "mdi:cog"
    _attr_name = "Configuration"
    _attr_unique_id = f"{DOMAIN}_configuration"

    def __init__(self, config_entry):
        self._config_entry = config_entry

        self._attr_device_info = {
            "identifiers": {(DOMAIN, config_entry.entry_id)},
            "name": "Daily Text",
            "entry_type": "service",
        }

    @property
    def native_value(self):
        """Return the primary state of the sensor."""
        return f"{self.language} / {self.months} / {self.strip_parentheses}"

    @property
    def extra_state_attributes(self):
        """Return additional attributes."""
        return {
            "strip_parentheses": self.strip_parentheses,
            "months": self.months,
            "language": self.language,
        }

    @property
    def language(self):
        return (
            self._config_entry.options.get(CONF_LANGUAGE)
            or self._config_entry.data.get(CONF_LANGUAGE)
        )

    @property
    def months(self):
        return (
            self._config_entry.options.get(CONF_MONTHS)
            or self._config_entry.data.get(CONF_MONTHS)
        )

    @property
    def strip_parentheses(self):
        return (
            self._config_entry.options.get(CONF_STRIP_PARENTHESES)
            if CONF_STRIP_PARENTHESES in self._config_entry.options
            else self._config_entry.data.get(CONF_STRIP_PARENTHESES, False)
        )
        
    async def async_config_entry_updated(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Appelé quand la config est modifiée pour mettre à jour l'entité."""
        self.async_write_ha_state()
