import json
import shutil
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

                    # Pokud script obsahuje metadata, použijeme jeho vlastní název.
                    # Jinak vytvoříme název z názvu souboru.
                    if pre_loaded[0].get("id") == "_meta":
                        script_name = pre_loaded[0].get("name", script_path.stem.replace("_", " ").title())
                    else:
                        script_name = script_path.stem.replace("_", " ").title()

                    pre_loaded_scripts.append({"script_name": script_name, "script_path": script_path})

            # Preloader slouží pouze k sestavení nabídky dostupných scriptů.
            # Vadné nebo nečitelné soubory proto přeskočíme a pokračujeme dalšími.
            except FileNotFoundError:
                continue

            except json.JSONDecodeError:
                continue

            except Exception:
                continue

            pre_loaded_scripts.sort(key=lambda script: script["script_name"].casefold())
    return pre_loaded_scripts


def script_loader(script_path, loaded_characters):

    script_path = Path(script_path)

    try:
        with open(script_path, encoding="utf-8") as soubor:

            script_data = json.load(soubor)

            # Strukturu souboru a dostupnost všech rolí ověřujeme předtím,
            # než z dat začneme vytvářet objekt Script.
            error = validate_script_data(script_data, loaded_characters)

            if error:
                return None, error

            # Metadata nejsou povinná. Pokud chybí, název scriptu odvodíme
            # z názvu souboru a autora ponecháme jako None.
            if script_data[0].get("id") == "_meta":

                meta = script_data[0]

                script_dict = {
                    "script_id": script_path.stem,
                    "script_name": meta.get("name", script_path.stem.replace("_", " ").title()),
                    "script_author": meta.get("author"),
                    "townsfolk": [],
                    "outsiders": [],
                    "minions": [],
                    "demons": [],
                    "travellers": [],
                    "fabled": [],
                    "loric": []
                }
                roles_data = script_data[1:]

            else:
                script_dict = {
                    "script_id": script_path.stem,
                    "script_name": script_path.stem.replace("_", " ").title(),
                    "script_author": None,
                    "townsfolk": [],
                    "outsiders": [],
                    "minions": [],
                    "demons": [],
                    "travellers": [],
                    "fabled": [],
                    "loric": []
                }
                roles_data = script_data

            # Validace už zaručila, že každé ID existuje v databázi,
            # takže zde můžeme role rovnou rozdělit do příslušných týmů.
            for role_data in roles_data:

                role_id = role_data["id"]
                character = loaded_characters[role_id]

                script_dict[character.team].append(character)

            return Script(script_dict), None

    except FileNotFoundError:
        return None, "Datový soubor nenalezen."

    except json.JSONDecodeError:
        return None, "Datový soubor je prázdný, nebo poškozený."

    except Exception as chyba:
        return None, f"Nastala neočekávaná chyba: {chyba}"


def validate_script_data(script_data, loaded_characters):

    if not isinstance(script_data, list):
        return "Datový soubor má chybnou datovou strukturu."

    if not script_data:
        return "Datový soubor je prázdný, nebo poškozený."

    roles_data = script_data

    # Metadata jsou volitelná a nejsou rolí, proto je před kontrolou
    # jednotlivých rolí ze seznamu vynecháme.
    if (
        isinstance(script_data[0], dict)
        and script_data[0].get("id") == "_meta"
    ):
        roles_data = script_data[1:]

    if not roles_data:
        return "Datový soubor neobsahuje žádné role."

    # Každá role musí být slovník s platným ID, které známe
    # z naší databáze postav.
    for role_data in roles_data:

        if not isinstance(role_data, dict):
            return "Datový soubor má chybnou datovou strukturu."

        if "id" not in role_data or not role_data["id"]:
            return "V datovém souboru se vyskytla role, která nemá ID."

        role_id = role_data["id"]

        if role_id not in loaded_characters:
            return f"Ve scriptu se vyskytla role, která není v databázi: {role_id}."

    return None


def import_script(source_path, loaded_characters):

    source_path = Path(source_path)

    try:
        with open(source_path, encoding="utf-8") as soubor:
            script_data = json.load(soubor)

        # Soubor nejdříve kompletně ověříme. Do složky aplikace se tak
        # dostane pouze script, se kterým aplikace umí pracovat.
        error = validate_script_data(
            script_data,
            loaded_characters
        )

        if error:
            return None, error

        destination_path = Path("scripts") / source_path.name

        # Existující scripty nepřepisujeme. Tím zároveň zabráníme pokusu
        # o kopírování souboru na sebe sama.
        if destination_path.exists():
            return None, f"Script '{source_path.name}' už existuje."

        shutil.copy(
            source_path,
            destination_path
        )

        return destination_path, None

    except FileNotFoundError:
        return None, "Vybraný soubor nebyl nalezen."

    except json.JSONDecodeError:
        return None, "Datový soubor je prázdný, nebo poškozený."

    except PermissionError:
        return None, "Soubor se nepodařilo zkopírovat kvůli nedostatečnému oprávnění."

    except Exception as chyba:
        return None, f"Nastala neočekávaná chyba: {chyba}"