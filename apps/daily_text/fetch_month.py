#fetch_month.py
import appdaemon.plugins.hass.hassapi as hass
from bs4 import BeautifulSoup
import requests
import os
import datetime
import json
from pathlib import Path
from dateutil.relativedelta import relativedelta

class FetchDailyText(hass.Hass):
    def initialize(self):
        self.log("FetchDailyText initialized")
        self.last_config_update = None 
        self.load_config()
        # Si aucune config chargeable, on réessaie dans 30s
        if self.lang_config == None:
            self.run_every(self.delayed_retry_config, now, 30)
            return

        self.listen_event(self.on_config_changed, "DAILY_TEXT_CONFIG_CHANGED")
        # appelle self.run_main tous les 7 jours (en secondes)
        now = datetime.datetime.now()
        self.run_every(self.run_main, now, 7 * 24 * 60 * 60)
        # exécuter tous les jours à 3h30 du matin.
        self.run_daily(self.scheduled_cleanup, datetime.time(3, 30, 0))
        # immédiat
        self.run_main({}) 

    def load_config(self):
        # Valeurs par défaut
        self.lang_code = "en"
        self.months_to_download = 1
        self.lang_config = None
        base_dir = Path(__file__).resolve().parent
        self.data_dir = base_dir / "data" / self.lang_code
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Lire la config depuis le capteur Home Assistant
        sensor_entity = "sensor.daily_text_configuration"
        state = self.get_state(sensor_entity, attribute="all")
        if not state:
            self.log(f"Sensor {sensor_entity} not found. Using default config.")
            return

        # Lecture des options
        attrs = state.get("attributes", {})
        self.lang_code = attrs.get("language", self.lang_code)
        self.months_to_download = int(attrs.get("months", self.months_to_download))

        # Recalcul du chemin avec la bonne langue
        self.data_dir = base_dir / "data" / self.lang_code
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Chargement du fichier de configuration des langues
        lang_file = base_dir / "lang" / f"{self.lang_code}.json"
        if not lang_file.exists():
            self.log(f"Language file not found: {lang_file}. Continuing with empty config.")
            self.lang_config = None
        else:
            with open(lang_file, encoding="utf-8") as f:
                self.lang_config = json.load(f)

        self.log(f"Loaded config: lang={self.lang_code}, months={self.months_to_download}")

    def on_config_changed(self, event_name, data, kwargs):
        # L'utilisateur a changé la configuration.
        self.log("Config changed event received.")
        # now = self.datetime()
        # if self.last_config_update and (now - self.last_config_update).total_seconds() < 2:
        #     self.log("Config update ignored (likely loop)", level="WARNING")
        #     return
        # self.last_config_update = now

        self.load_config()
        self.run_main({})

    def delayed_retry_config(self, kwargs):
        self.log("Retrying configuration load after delay...")
        self.load_config()
        if self.lang_config:
            self.listen_event(self.on_config_changed, "DAILY_TEXT_CONFIG_CHANGED")
            now = datetime.datetime.now()
            self.run_every(self.run_main, now, 7 * 24 * 60 * 60)
            self.run_daily(self.scheduled_cleanup, datetime.time(3, 30, 0))
            self.run_main({})
        else:
            self.log("Still no config available. Aborting retry.", level="WARNING")

    def run_main(self, kwargs):
        # Nettoyage des fichiers obsolètes
        today = datetime.date.today()
        self.clean_files(today)

        # Télécharger jusqu'à 4 mois à partir du mois courant
        for i in range(self.months_to_download):
            target_date = self.get_target_date(i)
            year, month = target_date.year, target_date.month

            if not self.should_fetch_month(year, month):
                self.log(f"Skipping {year}-{month:02d}, already downloaded.")
                continue

            self.download_month(year, month)
        self.fire_event("DAILY_TEXT_FILES_UPDATED", lang=self.lang_code)

    def clean_files(self, today):
        if not self.data_dir.exists():
            return

        # Déterminer la date max autorisée
        last_valid_date = today + relativedelta(months=self.months_to_download)
        
        for file in self.data_dir.glob("*.json"):
            try:
                date = datetime.date.fromisoformat(file.stem)
                
                # Fichier du passé
                if date < today:
                    file.unlink()
                    self.log(f"Deleted outdated file: {file.name}")
                # Fichier trop futur
                elif date >= last_valid_date:
                    file.unlink()
                    self.log(f"Deleted file beyond configured range: {file.name}")
            except Exception as e:
                self.log(f"Error while cleaning files: {e}", level="WARNING")


    # Exécuter tous les jours à 3h30 du matin.
    def scheduled_cleanup(self, kwargs):
        today = datetime.date.today()
        # Nettoyage des fichiers obsolètes
        self.clean_files(today)

    # Vérifie si tous les fichiers d’un mois existent
    def should_fetch_month(self, year, month):
        today = datetime.date.today()
        for day in range(1, 32):
            try:
                date = datetime.date(year, month, day)
            except ValueError:
                break
            if date < today:
                continue  # Ignore les jours passés
            file = self.data_dir / f"{date.isoformat()}.json"
            if not file.exists():
                return True
        return False

    # Téléchargement du texte pour un mois donné
    def download_month(self, year, month):
        month_index = month - 1  # 0-based
        doc_id = f"110{year}{200 + month_index}"
        url = f"{self.lang_config['url']}{doc_id}"
        self.log(f"Fetching from: {url}")
        today = datetime.date.today()

        try:
            response = requests.get(url)
            response.raise_for_status()
        except Exception as e:
            self.log(f"Failed to fetch page for {year}-{month:02d}: {e}", level="ERROR")
            return

        response.encoding = "utf-8"
        soup = BeautifulSoup(response.text, "html.parser")
        content_block = soup.find("div", class_="scalableui")
        if not content_block:
            self.log("Could not locate main content block.", level="ERROR")
            return

        elements = content_block.find_all(["header", "p", "div"], recursive=False)
        day = 1
        i = 0
        total_saved = 0

        while i < len(elements) - 2:
            try:
                h = elements[i]
                p = elements[i + 1]
                d = elements[i + 2]

                if h.name == "header" and h.find("h2") and p.name == "p" and d.get("class") == ["bodyTxt"]:
                    title = h.find("h2").get_text().replace("\u00A0", " ").strip()
                    #verse = self.extract_clean_text_from_html(p.get_text().replace("\u00A0", " ").strip())
                    verse = self.extract_clean_text_from_html(p)
                    body = self.extract_clean_text_from_html(d)

                    try:
                        date = datetime.date(year, month, day)
                    except ValueError:
                        break
                    if date < today:
                        day += 1 # Ignore les jours passés
                        i += 3
                        continue  

                    filename = date.isoformat() + ".json"
                    filepath = self.data_dir / filename
                    with open(filepath, "w", encoding="utf-8") as f:
                        json.dump({
                            "title": title,
                            "verse": verse,
                            "body": body
                        }, f, ensure_ascii=False, indent=2)

                    self.log(f"Saved: {filename}")
                    total_saved += 1
                    day += 1
                    i += 3
                else:
                    i += 1

            except Exception as e:
                self.log(f"Error at day {day}: {e}", level="WARNING")
                i += 1

        self.log(f"Download complete for {month:02d}/{year}: {total_saved} entries saved.")

    def extract_clean_text_from_html(self, element):
        """Transforme un bloc HTML en texte propre, en remplaçant certains liens par (*texte*)."""
        clone = BeautifulSoup(str(element), "html.parser")  # Traiter chaque lien dans la section
        for a in clone.find_all("a"):
            if not a.string:
                continue
            paren = self.first_paren_before(a)
            if paren == "(":
                continue  # Ne pas toucher si dans une parenthèse ouvrante
            else: # Sinon : première parenthèse est une parenthèse fermante ou rien → on remplace
                a.insert_before(f"(*{a.string}*)")
                a.decompose()
        return " ".join(clone.get_text().split()) # Récupérer le texte propre avec les liens remplacés

    #Date décalé par un offset de x-mois.
    def get_target_date(self, offset):
        today = datetime.date.today()
        return today + relativedelta(months=offset)

    def first_paren_before(self, tag):
        """Retourne la première parenthèse rencontrée avant le lien, ou None."""
        prev = tag.previous_sibling
        collected = ""

        # Rassembler le texte avant la balise
        while prev:
            if isinstance(prev, str):
                collected = prev + collected
            prev = prev.previous_sibling

        # On remonte la chaîne pour trouver la 1re parenthèse
        for c in reversed(collected):
            if c in ("(", ")"):
                return c
        return None
