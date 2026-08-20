from collections import Counter

import pytest

from character_loader import character_loader
from script_loader import script_loader
from player_count_loader import player_count_loader, get_player_count_setup
from generator import generate_setup

from conftest import (
    flatten,
    generate_success,
    ids,
    make_script,
    player_setup,
    result_bluffs,
    result_messages,
    result_teams,
)


def test_baron_adds_two_outsiders_and_removes_two_townsfolk(characters):
    script = make_script(
        characters,
        minions=("baron",),
        extra_townsfolk=9,
        extra_outsiders=5,
        extra_demons=1,
    )
    setup = player_setup(5, 0, 1, 1)

    result = generate_success(script, setup)
    teams = result_teams(result)

    assert len(teams["townsfolk"]) == 3
    assert len(teams["outsiders"]) == 2
    assert ids(teams["minions"]) == ["baron"]


def test_drunk_remove_self(characters):
    script = make_script(
        characters,
        outsiders=("drunk",),
        extra_townsfolk=10,
        extra_minions=1,
        extra_demons=1,
    )
    setup = player_setup(5, 1, 1, 1)

    result = generate_success(script, setup)
    teams = result_teams(result)

    assert "drunk" not in ids(teams["outsiders"])
    assert len(teams["townsfolk"]) == 6
    assert any("Opilec" in message for message in result_messages(result))


def test_fang_gu_adds_outsider(characters):
    script = make_script(
        characters,
        demons=("fanggu",),
        extra_townsfolk=10,
        extra_outsiders=5,
        extra_minions=1,
    )
    setup = player_setup(5, 0, 1, 1)

    result = generate_success(script, setup)
    teams = result_teams(result)

    assert len(teams["townsfolk"]) == 4
    assert len(teams["outsiders"]) == 1
    assert ids(teams["demons"]) == ["fanggu"]


def test_vigormortis_removes_outsider_if_possible(characters):
    script = make_script(
        characters,
        demons=("vigormortis",),
        extra_townsfolk=10,
        extra_outsiders=4,
        extra_minions=1,
    )
    setup = player_setup(4, 1, 1, 1)

    result = generate_success(script, setup)
    teams = result_teams(result)

    assert len(teams["outsiders"]) == 0
    assert len(teams["townsfolk"]) == 5


def test_village_idiot_never_exceeds_max_in_play(characters):
    vi = characters["villageidiot"]

    script = make_script(
        characters,
        townsfolk=("villageidiot",),
        extra_townsfolk=4,
        extra_outsiders=6,
        extra_minions=1,
        extra_demons=1,
    )
    # Všech 5 Townsfolk je v základním setupu, VI je tedy jistě ve hře.
    setup = player_setup(5, 0, 1, 1)

    result = generate_success(script, setup)
    teams = result_teams(result)
    count = ids(teams["townsfolk"]).count("villageidiot")

    assert 1 <= count <= vi.max_in_play
    assert len(flatten(teams)) == 7


def test_huntsman_adds_or_keeps_damsel(characters):
    if "huntsman" not in characters or "damsel" not in characters:
        pytest.skip("characters.json neobsahuje Huntsmana/Damsel.")

    script = make_script(
        characters,
        townsfolk=("huntsman",),
        outsiders=("damsel",),
        extra_townsfolk=4,
        extra_outsiders=6,
        extra_minions=1,
        extra_demons=1,
    )
    # Damsel není v základním setupu, Huntsman ano.
    setup = player_setup(5, 0, 1, 1)

    result = generate_success(script, setup)
    teams = result_teams(result)

    assert "damsel" in ids(teams["outsiders"])
    assert len(flatten(teams)) == 7


def test_summoner_results_in_no_demon_at_setup(characters):
    if "summoner" not in characters:
        pytest.skip("characters.json neobsahuje Summonera.")

    script = make_script(
        characters,
        minions=("summoner",),
        extra_townsfolk=10,
        extra_outsiders=5,
        extra_demons=2,
    )
    setup = player_setup(5, 0, 1, 1)

    result = generate_success(script, setup)
    teams = result_teams(result)

    assert teams["demons"] == []
    assert "summoner" in ids(teams["minions"])


def test_atheist_results_in_no_evil_characters(characters):
    if "atheist" not in characters:
        pytest.skip("characters.json neobsahuje Atheistu.")

    script = make_script(
        characters,
        townsfolk=("atheist",),
        extra_townsfolk=4,
        extra_outsiders=8,
        extra_minions=1,
        extra_demons=1,
    )
    setup = player_setup(5, 0, 1, 1)

    result = generate_success(script, setup)
    teams = result_teams(result)

    assert teams["minions"] == []
    assert teams["demons"] == []
    assert len(flatten(teams)) == 7
    assert result_bluffs(result) == []


@pytest.mark.parametrize("demon_id", ["kazali", "lordoftyphon"])
def test_no_minions_demons_remove_minions_from_setup(characters, demon_id):
    if demon_id not in characters:
        pytest.skip(f"characters.json neobsahuje {demon_id}.")

    script = make_script(
        characters,
        demons=(demon_id,),
        extra_townsfolk=12,
        extra_outsiders=6,
        extra_minions=3,
    )
    setup = player_setup(5, 1, 2, 1)

    result = generate_success(script, setup)
    teams = result_teams(result)

    assert teams["minions"] == []
    assert ids(teams["demons"]) == [demon_id]
    assert len(flatten(teams)) == 9


def test_legion_is_majority_and_has_at_least_two_good_players(characters):
    if "legion" not in characters:
        pytest.skip("characters.json neobsahuje Legii.")

    script = make_script(
        characters,
        demons=("legion",),
        extra_townsfolk=15,
        extra_outsiders=8,
        extra_minions=3,
    )
    # Normální 10-player rozdělení: 7 good / 3 evil.
    setup = player_setup(7, 0, 2, 1)

    result = generate_success(script, setup)
    teams = result_teams(result)

    legion_count = ids(teams["demons"]).count("legion")
    good_count = len(teams["townsfolk"]) + len(teams["outsiders"])

    assert legion_count == 7
    assert good_count == 3
    assert legion_count > good_count
    assert len(teams["outsiders"]) <= 2


def test_xaan_final_outsider_count_matches_message_x(characters):
    if "xaan" not in characters:
        pytest.skip("characters.json neobsahuje Xaana.")

    script = make_script(
        characters,
        minions=("xaan",),
        extra_townsfolk=12,
        extra_outsiders=6,
        extra_demons=1,
    )
    setup = player_setup(5, 1, 1, 1)

    result = generate_success(script, setup)
    teams = result_teams(result)
    messages = result_messages(result)

    x_messages = [message for message in messages if "Xaan" in message and "X =" in message]
    assert x_messages

    x_value = int(x_messages[0].split("X =")[-1].strip())
    assert len(teams["outsiders"]) == x_value


def test_boffin_generates_valid_setup(characters):
    if "boffin" not in characters:
        pytest.skip("characters.json neobsahuje Boffina.")

    script = make_script(
        characters,
        minions=("boffin",),
        extra_townsfolk=12,
        extra_outsiders=8,
        extra_demons=1,
    )

    setup = player_setup(5, 0, 1, 1)

    result = generate_success(script, setup)
    teams = result_teams(result)

    assert "boffin" in ids(teams["minions"])
    assert len(flatten(teams)) == 7


def test_bluffs_still_valid_after_modifiers(characters):
    script = make_script(
        characters,
        minions=("baron",),
        extra_townsfolk=12,
        extra_outsiders=7,
        extra_demons=1,
    )
    setup = player_setup(5, 0, 1, 1)

    result = generate_success(script, setup)
    in_play = set(ids(flatten(result_teams(result))))
    bluff_ids = set(ids(result_bluffs(result)))

    assert len(bluff_ids) == 3
    assert in_play.isdisjoint(bluff_ids)



def test_generation_failed():

    loaded_characters = character_loader()
    imp = loaded_characters["imp"]
    imp.setup_modifier["add"]["outsiders"] = 10
    script, error = script_loader("scripts/Potíže Přicházejí.json", loaded_characters)

    assert error is None
    assert script is not None

    player_setups = player_count_loader()
    player_setup = get_player_count_setup(player_setups, 13)

    generated_setup = generate_setup(script, player_setup)

    assert generated_setup.generation_failed


def test_godfather_special_modifier():

    loaded_characters = character_loader()
    script, error = script_loader("scripts/Čas Krvavého Měsíce.json", loaded_characters)

    assert error is None
    assert script is not None

    player_setups = player_count_loader()
    player_setup = get_player_count_setup(
        player_setups,
        14
    )

    add_outsider_spotted = False
    remove_outsider_spotted = False
    godfather_spotted = False

    for _ in range(1000):

        generated_setup = generate_setup(
            script,
            player_setup
        )

        if generated_setup.generation_failed:
            continue

        godfather_in_setup = any(
            character.character_id == "godfather"
            for character in generated_setup.generated_characters
        )

        if not godfather_in_setup:
            continue

        godfather_spotted = True

        townsfolk_count = len(
            generated_setup.teams["townsfolk"]
        )

        outsiders_count = len(
            generated_setup.teams["outsiders"]
        )

        minions_count = len(
            generated_setup.teams["minions"]
        )

        demons_count = len(
            generated_setup.teams["demons"]
        )

        # Godfather zvolil variantu:
        # +1 Outsider, -1 Townsfolk
        if outsiders_count == 2:

            add_outsider_spotted = True

            assert townsfolk_count == 8
            assert outsiders_count == 2
            assert minions_count == 3
            assert demons_count == 1

        # Godfather zvolil variantu:
        # -1 Outsider, +1 Townsfolk
        elif outsiders_count == 0:

            remove_outsider_spotted = True

            assert townsfolk_count == 10
            assert outsiders_count == 0
            assert minions_count == 3
            assert demons_count == 1

        # Jiný počet Outsiderů by znamenal chybu modifieru.
        else:
            assert False

    # Ověříme, že jsme během testu Godfathera skutečně vygenerovali
    # a že se náhodně objevily obě jeho varianty.
    assert godfather_spotted
    assert add_outsider_spotted
    assert remove_outsider_spotted


def test_vigormortis_conditional_modifier_with_outsider():

    loaded_characters = character_loader()
    script, error = script_loader("scripts/Sekty a Fialky.json", loaded_characters)

    assert error is None
    assert script is not None    

    player_setups = player_count_loader()

    # Základní setup pro 14 hráčů obsahuje jednoho Outsidera,
    # takže Vigormortis může použít variantu if_true.
    player_setup = get_player_count_setup(player_setups, 14)

    vigormortis_spotted = False

    # Generování je náhodné, proto potřebujeme více pokusů,
    # abychom spolehlivě narazili na Vigormortise.
    for _ in range(1000):

        generated_setup = generate_setup(script, player_setup)

        if generated_setup.generation_failed:
            continue

        vigormortis_in_setup = any(
            character.character_id == "vigormortis"
            for character in generated_setup.generated_characters
        )

        if not vigormortis_in_setup:
            continue

        vigormortis_spotted = True

        # Vigormortis: +1 Townsfolk, -1 Outsider.
        assert len(generated_setup.teams["townsfolk"]) == 10
        assert len(generated_setup.teams["outsiders"]) == 0
        assert len(generated_setup.teams["minions"]) == 3
        assert len(generated_setup.teams["demons"]) == 1

    # Test nesmí projít, pokud se Vigormortis vůbec nevygeneroval.
    assert vigormortis_spotted


def test_vigormortis_conditional_modifier_without_outsider():

    loaded_characters = character_loader()
    script, error = script_loader("scripts/Sekty a Fialky.json", loaded_characters)

    assert error is None
    assert script is not None    

    player_setups = player_count_loader()

    # Bez Outsidera nelze if_true provést,
    # takže se musí použít prázdná varianta if_false.
    player_setup = get_player_count_setup(player_setups, 13)

    vigormortis_spotted = False

    for _ in range(1000):

        generated_setup = generate_setup(script, player_setup)

        if generated_setup.generation_failed:
            continue

        vigormortis_in_setup = any(
            character.character_id == "vigormortis"
            for character in generated_setup.generated_characters
        )

        if not vigormortis_in_setup:
            continue

        vigormortis_spotted = True

        # Rozdělení týmů musí zůstat beze změny.
        assert len(generated_setup.teams["townsfolk"]) == 9
        assert len(generated_setup.teams["outsiders"]) == 0
        assert len(generated_setup.teams["minions"]) == 3
        assert len(generated_setup.teams["demons"]) == 1

    assert vigormortis_spotted