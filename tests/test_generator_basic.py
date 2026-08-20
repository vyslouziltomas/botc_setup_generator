import random

from conftest import (
    flatten,
    generate_success,
    ids,
    make_script,
    player_setup,
    result_bluffs,
    result_failed,
    result_teams,
)


def test_basic_setup_keeps_player_count(characters):
    script = make_script(
        characters,
        extra_townsfolk=8,
        extra_outsiders=4,
        extra_minions=3,
        extra_demons=2,
    )
    setup = player_setup(5, 1, 1, 1)

    result = generate_success(script, setup)
    teams = result_teams(result)

    assert len(flatten(teams)) == 8


def test_basic_setup_contains_only_player_teams(characters):
    script = make_script(
        characters,
        extra_townsfolk=8,
        extra_outsiders=4,
        extra_minions=3,
        extra_demons=2,
    )
    setup = player_setup(5, 1, 1, 1)

    result = generate_success(script, setup)

    assert set(result_teams(result)) == {
        "townsfolk",
        "outsiders",
        "minions",
        "demons",
    }


def test_bluffs_are_not_in_play(characters):
    script = make_script(
        characters,
        extra_townsfolk=10,
        extra_outsiders=5,
        extra_minions=2,
        extra_demons=1,
    )
    setup = player_setup(5, 1, 1, 1)

    result = generate_success(script, setup)
    in_play = set(ids(flatten(result_teams(result))))
    bluffs = ids(result_bluffs(result))

    assert len(bluffs) == 3
    assert not in_play.intersection(bluffs)


def test_drunk_and_lunatic_are_never_bluffs(characters):
    # Pokud role nejsou na scriptu, nemohou se bluffem stát tak jako tak;
    # zde je přidáme mezi dostupné good role.
    script = make_script(
        characters,
        townsfolk=(),
        outsiders=("drunk", "lunatic"),
        extra_townsfolk=10,
        extra_outsiders=4,
        extra_minions=2,
        extra_demons=1,
    )
    setup = player_setup(5, 0, 1, 1)

    result = generate_success(script, setup)
    bluff_ids = set(ids(result_bluffs(result)))

    assert "drunk" not in bluff_ids
    assert "lunatic" not in bluff_ids


def test_insufficient_script_returns_failed_setup(characters):
    script = make_script(
        characters,
        extra_townsfolk=2,
        extra_outsiders=1,
        extra_minions=1,
        extra_demons=1,
    )
    setup = player_setup(5, 1, 1, 1)

    random.seed(0)
    result = __import__("conftest").generate_setup(script, setup)

    assert result_failed(result) is True
