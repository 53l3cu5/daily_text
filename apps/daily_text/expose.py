#expose.py
from base import BaseDailyText, clean_body, replace_bible_references
from datetime import time

class ExposeDailyTextLovelace(BaseDailyText):

    def initialize(self):
        self.log("Initializing ExposeDailyTextLovelace...")
        super().initialize()
        self.listen_event(self.on_text_updated, "DAILY_TEXT_FILES_UPDATED")
        self.run_daily(self.publish_text, time(0, 0, 2)) #MAJ à 0h02 tous les jours

    def on_text_updated(self, event_name, data, kwargs):
        self.log("DAILY_TEXT_FILES_UPDATED received, refreshing sensor...")
        self.publish_text({})

    def publish_text(self, kwargs):
        filepath, today = self.get_file_for_today()#"2025-08-07.json")
        if not filepath.exists():
            self.set_error_state("sensor.daily_text_lovelace", "No text available", today)
            return

        data, error = self.read_json_file(filepath)
        if error:
            self.set_error_state("sensor.daily_text_lovelace", "JSON reading error", today)
            self.error(error)
            return

        title = data.get("title", "Daily text")
        verse = data.get("verse", "").replace("(*", "").replace("*)", "")
        body = data.get("body", "").replace("(*", "").replace("*)", "")

        self.set_state("sensor.daily_text_lovelace", state=title, attributes={
            "title": title,
            "verse": verse,
            "comment": body,
            "date": today.isoformat(),
            "friendly_name": "Daily text for Lovelace"
        })
        self.log("Daily text for Lovelace exposed.")
        
class ExposeDailyTextTTS(BaseDailyText):

    def initialize(self):
        self.log("Initializing ExposeDailyTextTTS...")
        self.last_config_update = None 
        self.listen_event(self.on_text_updated_tts, "DAILY_TEXT_FILES_UPDATED")
        super().initialize()
        self.run_daily(self.publish_text_tts, time(0, 0, 3)) #MAJ à 0h03 tous les jours

    def on_text_updated_tts(self, event_name, data, kwargs):
        self.log("DAILY_TEXT_FILES_UPDATED received, refreshing sensor...")
        self.publish_text_tts({})

    def publish_text_tts(self, kwargs):
        filepath, today = self.get_file_for_today()#"2025-08-07.json")
        if not filepath.exists():
            self.set_error_state("sensor.daily_text_tts", "No text available", today)
            return

        data, error = self.read_json_file(filepath)
        if error:
            self.set_error_state("sensor.daily_text_tts", "JSON reading error", today)
            self.error(error)
            return

        title = data.get("title", "Texte du jour")
        #verse = data.get("verse", "")
        verse = replace_bible_references(data.get("verse", ""), self.lang_config, True)
        #body = clean_body(self, data.get("body", ""))
        body = replace_bible_references(clean_body(self, data.get("body", "")), self.lang_config, self.strip_parentheses)

        tts = f"{title}\n{verse}\n{body}"
        if not tts.endswith("."):
            tts += "."

        #full_tts = replace_bible_references(tts, self.lang_config, False)

        self.set_state("sensor.daily_text_tts", state=title, attributes={
            #"tts_full": full_tts,
            "tts_full": tts,
            "date": today.isoformat(),
            "friendly_name": "Daily text for text to speech"
        })
        self.log("Daily text for TTS exposed.")
