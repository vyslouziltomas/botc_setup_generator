from character_loader import character_loader
from script_loader import script_loader
from player_count_loader import player_count_loader, get_player_count_setup
from generator import generate_setup


def test_setup_is_valid():
    loaded_characters = character_loader()
    script, error = script_loader(
        "scripts/Potíže Přicházejí.json",
        loaded_characters
    )

    assert error is None
    assert script is not None

    player_setups = player_count_loader()
    player_setup = get_player_count_setup(player_setups, 15)

    successful_generations = 0

    for _ in range(1000):
        generated_setup = generate_setup(script, player_setup)

        if generated_setup.generation_failed:
            continue

        total = (
            len(generated_setup.teams["townsfolk"])
            + len(generated_setup.teams["outsiders"])
            + len(generated_setup.teams["minions"])
            + len(generated_setup.teams["demons"])
        )

        assert total == 15

        bluffs = generated_setup.bluffs
        assert len(bluffs) == 3

        for bluff in bluffs:
            assert bluff.character_id != "drunk"
            assert bluff not in generated_setup.generated_characters

        successful_generations += 1

    assert successful_generations > 0