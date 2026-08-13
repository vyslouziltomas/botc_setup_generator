from character_loader import character_loader
from script_loader import script_loader
from player_count_loader import player_count_loader, get_player_count_setup
from generator import generate_setup

def test_setup_is_valid():
    loaded_characters = character_loader()
    script = script_loader("scripts/trouble_brewing.json", loaded_characters)

    player_setups = player_count_loader()
    player_setup = get_player_count_setup(player_setups, 15)

    successful_generations = 0

    for _ in range(1000):
        generated_setup = generate_setup(script, player_setup)

        if generated_setup.generation_failed:
            continue

        total = len(generated_setup.teams["townsfolk"]) + len(generated_setup.teams["outsiders"]) + len(generated_setup.teams["minions"]) + len(generated_setup.teams["demons"])
        assert total == 15

        bluffs = generated_setup.bluffs
        assert len(bluffs) == 3

        for bluff in bluffs:
            assert bluff.character_id != "drunk"
            assert bluff not in generated_setup.generated_characters

        successful_generations += 1

    assert successful_generations > 0

def test_drunk_modifier():

    loaded_characters = character_loader()
    script = script_loader("scripts/trouble_brewing.json", loaded_characters)

    player_setups = player_count_loader()
    player_setup = get_player_count_setup(player_setups, 15)

    drunk_spotted = False

    for _ in range(1000):
        generated_setup = generate_setup(script, player_setup)

        if generated_setup.generation_failed:
            continue

        elif generated_setup.message:
            drunk_spotted = True

            for character in generated_setup.generated_characters:
                assert character.character_id != "drunk"

            assert "Jeden měšťan je Opilec." in generated_setup.message
            assert len(generated_setup.teams["townsfolk"]) in (8, 10)
    
    assert drunk_spotted

def test_baron_modifier():

    loaded_characters = character_loader()
    script = script_loader("scripts/trouble_brewing.json", loaded_characters)

    player_setups = player_count_loader()
    player_setup = get_player_count_setup(player_setups, 13)

    baron_spotted = False

    for _ in range(1000):
        generated_setup = generate_setup(script, player_setup)

        if generated_setup.generation_failed:
            continue

        baron_in_setup = any(
            character.character_id == "baron"
            for character in generated_setup.generated_characters
        )

        if baron_in_setup:
            baron_spotted = True

            if generated_setup.message:
                assert len(generated_setup.teams["townsfolk"]) == 8
                assert len(generated_setup.teams["outsiders"]) == 1
                assert len(generated_setup.teams["minions"]) == 3
                assert len(generated_setup.teams["demons"]) == 1

            else:
                assert len(generated_setup.teams["townsfolk"]) == 7
                assert len(generated_setup.teams["outsiders"]) == 2
                assert len(generated_setup.teams["minions"]) == 3
                assert len(generated_setup.teams["demons"]) == 1 

    assert baron_spotted


def test_generation_failed():

    loaded_characters = character_loader()
    imp = loaded_characters["imp"]
    imp.setup_modifier["add"]["outsiders"] = 10
    script = script_loader("scripts/trouble_brewing.json", loaded_characters)

    player_setups = player_count_loader()
    player_setup = get_player_count_setup(player_setups, 13)

    generated_setup = generate_setup(script, player_setup)

    assert generated_setup.generation_failed