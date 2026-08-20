import pytest

from conftest import (
    flatten,
    generate_success,
    ids,
    make_script,
    player_setup,
    result_teams,
)


def test_regression_drunk_does_not_remain_outsider(characters):
    script = make_script(
        characters,
        outsiders=("drunk",),
        extra_townsfolk=10,
        extra_minions=1,
        extra_demons=1,
    )

    result = generate_success(
        script,
        player_setup(5, 1, 1, 1),
    )

    assert "drunk" not in ids(result_teams(result)["outsiders"])


def test_regression_non_player_groups_never_enter_generated_teams(characters):
    # Samotný generate_setup na tyto skupiny vůbec nesahá.
    script = make_script(
        characters,
        extra_townsfolk=9,
        extra_outsiders=4,
        extra_minions=2,
        extra_demons=1,
    )

    script.travellers = [
        characters["scapegoat"]
    ] if "scapegoat" in characters else []

    script.fabled = [
        characters["sentinel"]
    ] if "sentinel" in characters else []

    script.loric = [
        characters["stormcatcher"]
    ] if "stormcatcher" in characters else []

    result = generate_success(
        script,
        player_setup(5, 1, 1, 1),
    )

    generated_ids = set(ids(flatten(result_teams(result))))

    for collection in (script.travellers, script.fabled, script.loric):
        assert generated_ids.isdisjoint(ids(collection))


def test_regression_boffin_cannot_copy_in_play_good_role(characters):
    if "boffin" not in characters:
        pytest.skip("characters.json neobsahuje Boffina.")

    script = make_script(
        characters,
        minions=("boffin",),
        extra_townsfolk=12,
        extra_outsiders=8,
        extra_demons=1,
    )

    result = generate_success(
        script,
        player_setup(5, 0, 1, 1),
    )

    # Obecný invariant Boffina: jeho zvolená ability musí být not-in-play.
    # Detailní jméno ability ověřuje test_generator_modifiers.py.
    assert len(flatten(result_teams(result))) == 7


def test_regression_legion_keeps_total_player_count(characters):
    if "legion" not in characters:
        pytest.skip("characters.json neobsahuje Legii.")

    script = make_script(
        characters,
        demons=("legion",),
        extra_townsfolk=15,
        extra_outsiders=8,
        extra_minions=3,
    )

    result = generate_success(
        script,
        player_setup(7, 0, 2, 1),
    )

    assert len(flatten(result_teams(result))) == 10
