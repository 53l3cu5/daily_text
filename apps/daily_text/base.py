#base.py
import appdaemon.plugins.hass.hassapi as hass
from datetime import time
from pathlib import Path
import json
import re

# -------------------- Classe de base --------------------

class BaseDailyText(hass.Hass):

    def initialize(self):
        self.lang_code = "en"  # valeur par défaut
        self.months = 1        # valeur par défaut
        self.load_config_from_entity()
        self.listen_state(self.on_config_changed, "sensor.daily_text_configuration")


    def on_config_changed(self, entity, attribute, old, new, **kwargs):
        self.log("Configuration change detected, reloading...")
        self.load_config_from_entity()

        # Si la classe enfant a une méthode fetch_texts, on l'appelle
        if hasattr(self, "fetch_texts") and callable(self.fetch_texts):
            self.fetch_texts()

    def load_config_from_entity(self):
        entity_id = "sensor.daily_text_configuration"
        state = self.get_state(entity_id, attribute="all")

        if not state or "attributes" not in state:
            self.error(f"Failed to load config from {entity_id}")
            return

        # Mémorise et partage les paramètre
        attributes = state["attributes"]
        self.lang_code = attributes.get("language", "en")
        self.months = int(attributes.get("months", 1))
        self.strip_parentheses = attributes.get("strip_parentheses", False)

        lang_file = Path(__file__).resolve().parent / "lang" / f"{self.lang_code}.json"
        if not lang_file.exists():
            self.error(f"Language file not found: {lang_file}")
            self.lang_config = {}
        else:
            with open(lang_file, encoding="utf-8") as f:
                self.lang_config = json.load(f)

        self.fire_event("DAILY_TEXT_CONFIG_CHANGED")
        self.log(f"Configuration loaded: lang = {self.lang_code}, months = {self.months}")

    def get_file_for_today(self, force_filename=None):
        today = self.datetime().date()
        filename = force_filename or f"{today:%Y-%m-%d}.json"
        data_dir = Path(__file__).resolve().parent / "data" / self.lang_code
        filepath = data_dir / filename
        return filepath, today

    def read_json_file(self, filepath):
        try:
            with open(filepath, encoding="utf-8") as f:
                return json.load(f), None
        except Exception as e:
            return None, str(e)

    def set_error_state(self, entity, message, date):
        self.set_state(entity, state=message, attributes={
            "friendly_name": entity.replace("_", " ").title(),
            "date": date.isoformat()
        })
        self.log(message)


# -------------------- Fonctions utilitaires --------------------

def clean_body(self, text: str) -> str:
    """
    Nettoie le corps du texte pour une lecture vocale plus fluide.
    Il supprime les références entre le dernier et l'avant-dernier point final.
    Le seuil de séparation dépend de la langue (paramètre tts_split_threshold).
    """
    threshold = self.lang_config.get("tts_split_threshold", 3)  # valeur par défaut à 3
    point_positions = [m.start() for m in re.finditer(r'\.', text)] # Trouver tous les points finaux dans la chaîne
    if len(point_positions) < threshold:
        return text.strip()  # Pas assez de points, on ne modifie rien
    cut_position = point_positions[-threshold] + 1 # On garde tout jusqu'au 3ᵉ point en partant de la fin
    return text[:cut_position].strip()

def clean_part(text):# Nettoyage des espaces insécables 
    text = text.replace('\u00A0', ' ')
    return ''.join(c for c in text if c.isprintable()).strip()

def try_add(a, b):
    try:
        if int(a)+1 == int(b):
            return f"{a}-{b}"
    except ValueError:
        return None  # Conversion impossible
    return None

def merge_pairs(lst):
    i = 0
    while i < len(lst) - 1:
        #print(f"i: {i}  len(lst) - 1: {len(lst) - 1}")
        res = try_add(lst[i], lst[i+1])
        #print(f"try_add(lst[i], lst[i+1]) : {lst[i]} , {lst[i+1]} = res : {res}")
        if res is not None:
            lst[i] = res      # remplace la case i par la somme
            del lst[i+1]      # supprime la case i+1
            # ne pas incrémenter i car après suppression la prochaine paire commence à i+1
        else:
            i += 1            # on passe à la suivante
    return lst

# Fonction de conversion d'une référence
def convert_ref(ref, lang_config):
    ref = ref.strip()
    for book in sorted(lang_config["book_names"], key=len, reverse=True):
        if ref.startswith(book):
            long_book = lang_config["book_names"][book]
            rest = ref[len(book):].strip()

            if ':' not in rest:
                chapter = ""  # cas rare : versets seul
                verses = rest
            else:
                chapter, verses = rest.split(":", 1)
                chapter = f"{long_book} {chapter}, "
            verses = verses.strip()

            parts = [v.strip() for v in verses.split(",")]
            parts = merge_pairs(parts)
            joined = []
            for part in parts:
                if "-" in part:
                    start, end = [v.strip() for v in part.split("-", 1)]
                    joined.append(f"{start} {lang_config['to']} {end}")
                else:
                    joined.append(part)

            if len(joined) > 1:
                joined_text = f"{lang_config['verse_plural']} {', '.join(joined[:-1])} {lang_config['and']} {joined[-1]}"
            else:
                joined_text = f"{lang_config['verse_singular']} {joined[0]}"

            return f"{chapter}{joined_text}"
    return ref  # pas reconnu

# Fonction de conversion de plusieurs références
def convert_multiple_refs(ref_string, lang_config):
    ref_string = ref_string.strip()
    starred = "*" in ref_string  # repère si c’est un lien transformé
    parts = [part.strip("* ") for part in ref_string.split(";")]

    result = []
    last_book = None
    #print(f"len(parts): {len(parts)}")
    #print(f"parts: {parts}")
    for part in parts:
        part = clean_part(part)
        #print(f"part: {part}")

        matched = False
        for book in sorted(lang_config["book_names"], key=len, reverse=True):
            if part.startswith(book):
                #print(f"book: {book}")
                last_book = book
                result.append(convert_ref(part, lang_config))
                matched = True
                break

        #print(f"not matched: {not matched} and last_book: {last_book}")
        if not matched and last_book: 
            # Même livre, mais nouveau chapitre
            reconstructed = f"{last_book} {part}"
            converted = convert_ref(reconstructed, lang_config)
            
            # Ajouter "puis chapitre" pour TTS fluide
            converted = converted.replace(lang_config["book_names"][last_book], lang_config["then_chapter"], 1) # Remplacer une seule fois
            result.append(converted)
        elif not matched:
            result.append(part) # Livre inconnu ou impossible à reconstruire

    if starred:
        return f" {'; '.join(result)}"
    else:
        return f". ( {'; '.join(result)} )"

def replace_bible_references(text, lang_config, preserve_non_starred=True):
    def repl(match):
        content = match.group(1)
        if "*" in content:
            # Référence cliquable → on garde toujours
            return convert_multiple_refs(content, lang_config)
        elif preserve_non_starred:
            # Comportement habituel (on garde les parenthèses avec la conversion)
            return convert_multiple_refs(content, lang_config)
        else:
            # On supprime complètement la référence
            return ""
        
    return re.sub(r'\(([^()]+)\)', repl, text)


