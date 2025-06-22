from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from .const import DOMAIN

PLATFORMS = ["sensor"]

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    return True

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][config_entry.entry_id] = config_entry.data

    # Lance la configuration de la ou des plateformes
    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    # Décharge la ou les plateformes
    unloaded = await hass.config_entries.async_unload_platforms(config_entry, PLATFORMS)

    # Nettoyage des données
    if unloaded:
        hass.data[DOMAIN].pop(config_entry.entry_id, None)

    return unloaded
