[![Static Badge](https://img.shields.io/badge/HACS-Custom-41BDF5?style=for-the-badge&logo=homeassistantcommunitystore&logoColor=white)](https://github.com/hacs/integration) 
![GitHub Downloads (all assets, all releases)](https://img.shields.io/github/downloads/53l3cu5/daily_text/total?style=for-the-badge)
![GitHub Issues or Pull Requests](https://img.shields.io/github/issues/53l3cu5/daily_text?style=for-the-badge) 



![GitHub Release Date](https://img.shields.io/github/release-date-pre/53l3cu5/daily_text?style=for-the-badge&label=Latest%20Beta%20Release) [![GitHub Release](https://img.shields.io/github/v/release/53l3cu5/daily_text?include_prereleases&style=for-the-badge)](https://github.com/53l3cu5/daily_text/releases)

<!--![GitHub Release Date](https://img.shields.io/github/release-date/53l3cu5/daily_text?style=for-the-badge&label=Latest%20Release) [![GitHub Release](https://img.shields.io/github/v/release/53l3cu5/daily_text?style=for-the-badge)](https://github.com/53l3cu5/daily_text/releases)-->

![Validate HACS](https://github.com/53l3cu5/daily_text/actions/workflows/validate-hacs.yml/badge.svg)
# Daily text
Automatically displays and reads the daily Bible text from jw.org in Home Assistant, with multilingual support and offline access.

## 🗣️ Voice Integration

This project was primarily designed for **Home Assistant Voice** and its native Assist functionality.

While it can technically be used with other voice satellites or TTS systems, this is not the main goal of the project and support for alternative setups may be limited.

## 🌐 Language Support

The user interface is currently available in **English** and **French**.

If you would like to help translate the project into another language, you're welcome to contribute!  
Please feel free to open an issue or start a discussion — we’ll work together to add support for your language.

## 📦 Dependencies and Installation

Before installing this integration, please make sure you have the following prerequisites set up:

- **HACS (Home Assistant Community Store)**:  
  The preferred way to install and manage this integration.  
  Learn more and install HACS here: [https://www.hacs.xyz](https://www.hacs.xyz)

- **AppDaemon**:  
  Required for running the backend app that handles the daily text processing.  
  Installation instructions can be found at: [https://github.com/hassio-addons/addon-appdaemon/blob/main/appdaemon/DOCS.md](https://github.com/hassio-addons/addon-appdaemon/blob/main/appdaemon/DOCS.md)

Make sure both HACS and AppDaemon are properly installed and configured before using this project.

- ### 🧩 Making Daily Text visible in HACS

  To make sure the **Daily Text** AppDaemon app appears in your HACS dashboard and can be easily installed, you need to enable AppDaemon apps discovery in HACS settings.

  If you don’t see this app listed in HACS:

  1. Open Home Assistant and go to **Settings > Devices & Services**.
  2. Select **HACS** from the list.
  3. Click **Configure**.
  4. Find and enable the option **Enable AppDaemon apps discovery & tracking**.
  5. Save the settings.

  After that, the Daily Text app will be visible in HACS, making installation and updates straightforward.

  For more information, see the official HACS documentation:  
  [Making AppDaemon Apps Visible in HACS](https://www.hacs.xyz/docs/use/repositories/type/appdaemon/#making-appdaemon-apps-visible-in-hacs)


## 📜 License

This project is licensed under the **Creative Commons Attribution - NonCommercial - ShareAlike 4.0 International (CC BY-NC-SA 4.0)**.

This means you are free to copy, modify, and redistribute it, provided that you:
- **give appropriate credit** to the original author,
- **do not use it for commercial purposes**,
- **distribute your contributions under the same license**.

⚠️ Any commercial use is prohibited without explicit permission.

