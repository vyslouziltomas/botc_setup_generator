from character_loader import character_loader
from script_loader import script_loader
from player_count_loader import player_count_loader, get_player_count_setup
from generator import generate_setup

def test_setup_is_valid():
    loaded_characters = character_loader()
    script = script_loader("scripts/Potíže Přicházejí.json", loaded_characters)

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
    script = script_loader("scripts/Potíže Přicházejí.json", loaded_characters)

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
    script = script_loader("scripts/Potíže Přicházejí.json", loaded_characters)

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
    script = script_loader("scripts/Potíže Přicházejí.json", loaded_characters)

    player_setups = player_count_loader()
    player_setup = get_player_count_setup(player_setups, 13)

    generated_setup = generate_setup(script, player_setup)

    assert generated_setup.generation_failed


def test_godfather_special_modifier():

    loaded_characters = character_loader()
    script = script_loader(
        "scripts/Čas Krvavého Měsíce.json",
        loaded_characters
    )

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
    script = script_loader(
        "scripts/Sekty a Fialky.json",
        loaded_characters
    )

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
    script = script_loader(
        "scripts/Sekty a Fialky.json",
        loaded_characters
    )

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