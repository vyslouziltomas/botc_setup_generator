import json
from player_count_setup import PlayerCountSetup


def player_count_loader():

    player_setups = {}

    try:
        with open("player_count_setups.json", encoding="utf-8") as soubor:

            setup_data = json.load(soubor)

            for polozka in setup_data:

                setup = PlayerCountSetup(polozka)

                player_setups[polozka["player_count"]] = setup

            return player_setups

    except FileNotFoundError:
        print("Soubor s nastavením hráčů nebyl nalezen.")
        return {}

    except json.JSONDecodeError:
        print("Soubor s nastavením hráčů je prázdný nebo poškozený.")
        return {}

    except Exception as chyba:
        print(f"Nastala neočekávaná chyba: {chyba}")
        return {}


def get_player_count_setup(player_setups, number_of_players):

    return player_setups.get(number_of_players)