from character_loader import character_loader
from script_loader import script_loader
from player_count_loader import player_count_loader, get_player_count_setup
from generator import generate_setup

def application(script_path, number_of_players):

    loaded_characters = character_loader()

    script = script_loader(script_path, loaded_characters)

    player_setups = player_count_loader()

    player_setup = get_player_count_setup(player_setups, number_of_players)
    if player_setup is None:
        error = "Pro tento počet hráčů neexistuje nastavení."
        return None, error
    
    error = script.validate(player_setup)
    if error:
        return None, error

    for _ in range(20):
        generated_setup = generate_setup(script, player_setup)
        if not generated_setup.generation_failed:
            break
    if generated_setup.generation_failed:
        return None, "Generování selhalo."

    return generated_setup, None