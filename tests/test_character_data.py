import json
from collections import Counter
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _raw_characters():
    return json.loads(
        (PROJECT_ROOT / "characters.json").read_text(encoding="utf-8")
    )


def test_character_ids_are_unique():
    data = _raw_characters()
    ids = [item["character_id"] for item in data]

    duplicates = [
        character_id
        for character_id, count in Counter(ids).items()
        if count > 1
    ]

    assert duplicates == []


def test_every_character_has_required_structure():
    required = {
        "character_id",
        "name_en",
        "name_cs",
        "team",
        "setup_modifier",
    }

    for item in _raw_characters():
        assert required.issubset(item), item.get("character_id")
        assert "add" in item["setup_modifier"], item["character_id"]
        assert "remove" in item["setup_modifier"], item["character_id"]


def test_team_names_are_supported():
    supported = {
        "townsfolk",
        "outsiders",
        "minions",
        "demons",
        "travellers",
        "fabled",
        "loric",
    }

    found = {item["team"] for item in _raw_characters()}

    assert found <= supported


@pytest.mark.parametrize(
    ("character_id", "special_type"),
    [
        ("drunk", "remove_self"),
        ("villageidiot", "duplicate_self"),
        ("huntsman", "add_specific_character"),
        ("boffin", "copy_good_ability"),
        ("summoner", "no_demon"),
        ("atheist", "no_evil"),
        ("xaan", "x_outsiders"),
        ("kazali", "no_minions"),
        ("lordoftyphon", "no_minions"),
        ("legion", "legion"),
    ],
)
def test_known_special_modifier_mapping(character_id, special_type):
    data = {
        item["character_id"]: item
        for item in _raw_characters()
    }

    if character_id not in data:
        pytest.skip(f"characters.json neobsahuje {character_id}.")

    special = data[character_id]["setup_modifier"].get("special")

    assert special is not None
    assert special["type"] == special_type


def test_village_idiot_max_in_play():
    data = {
        item["character_id"]: item
        for item in _raw_characters()
    }

    if "villageidiot" not in data:
        pytest.skip("characters.json neobsahuje Village Idiota.")

    assert data["villageidiot"].get("max_in_play", 1) == 3


def test_legion_max_in_play():
    data = {
        item["character_id"]: item
        for item in _raw_characters()
    }

    if "legion" not in data:
        pytest.skip("characters.json neobsahuje Legii.")

    assert data["legion"].get("max_in_play", 1) == 11
