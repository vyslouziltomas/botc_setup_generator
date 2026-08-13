import json
from pathlib import Path
from script import Script

def pre_loader():

    path_folder = Path("scripts")
    pre_loaded_scripts = []

    for script_path in path_folder.iterdir():

        if script_path.suffix.lower() == ".json":

            try:
                with open(script_path, encoding="utf-8") as soubor:

                    pre_loaded = json.load(soubor)

                    if not pre_loaded:
                        continue

                    if pre_loaded[0].get("id") == "_meta":                    
                        script_name = pre_loaded[0].get("name", script_path.stem.replace("_", " ").title())                    
                    else:
                        script_name = script_path.stem.replace("_", " ").title()

                    pre_loaded_scripts.append({"script_name": script_name, "script_path": script_path})

            except FileNotFoundError:
                continue
            
            except json.JSONDecodeError:
                print("Datový soubor je prázdný, nebo poškozený.")
                continue

            except Exception as chyba:
                print(f"Nastala neočekávaná chyba: {chyba}")
                continue

    return pre_loaded_scripts


def script_loader(script_path, loaded_characters):

    script_path = Path(script_path)
    
    try:
        with open(script_path, encoding="utf-8") as soubor:

            script_data = json.load(soubor)

            if not script_data:
                print("Datový soubor neobsahuje žádné role.")
                return None

            if script_data[0].get("id") == "_meta":

                meta = script_data[0]

                script_dict = {
                    "script_id": Path(script_path).stem,
                    "script_name": meta.get("name", script_path.stem.replace("_", " ").title()),
                    "script_author": meta.get("author"),
                    "townsfolk": [],
                    "outsiders": [],
                    "minions": [],
                    "demons": []
                }
                roles_data = script_data[1:]
                
            else:
                script_dict = {
                    "script_id": Path(script_path).stem,
                    "script_name": Path(script_path).stem.replace("_", " ").title(),
                    "script_author": None,
                    "townsfolk": [],
                    "outsiders": [],
                    "minions": [],
                    "demons": []
                }
                roles_data = script_data


            for role_data in roles_data:

                role_id = role_data["id"]
                character = loaded_characters.get(role_id)

                if character is None:
                    print("Ve skriptu se vyskytla role, která není v databázi.")
                    return None
                
                if character.team == "townsfolk":
                    script_dict["townsfolk"].append(character)
                
                elif character.team == "outsider":
                    script_dict["outsiders"].append(character)
                
                elif character.team == "minion":
                    script_dict["minions"].append(character)

                elif character.team == "demon":
                    script_dict["demons"].append(character)

            return Script(script_dict)


    except FileNotFoundError:
        return None
    
    except json.JSONDecodeError:
        print("Datový soubor je prázdný, nebo poškozený.")
        return None

    except Exception as chyba:
        print(f"Nastala neočekávaná chyba: {chyba}")
        return None
    

