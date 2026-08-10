import json
from character import Character

def character_loader():

    loaded_characters = {}

    try:
        with open("characters.json", encoding="utf-8") as soubor:

            characters_data = json.load(soubor)

            for polozka in characters_data:

                character = Character(polozka)

                loaded_characters[polozka["character_id"]] = character

            return loaded_characters
        
    except FileNotFoundError:
        print("SCRIPT SOUBOR NENALEZEN")
        return {}
    
    except json.JSONDecodeError:
        print("Datový soubor je prázdný, nebo poškozený.")
        return {}

    except Exception as chyba:
        print(f"Nastala neočekávaná chyba: {chyba}")
        return {}