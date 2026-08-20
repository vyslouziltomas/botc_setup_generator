import json
from pathlib import Path

import pytest

from script_loader import pre_loader, script_loader, validate_script_data


def _write_script(path, role_ids, *, meta=True):
    data = []

    if meta:
        data.append({
            "id": "_meta",
            "name": "Test Script",
            "author": "pytest",
        })

    data.extend({"id": role_id} for role_id in role_ids)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def test_validate_rejects_unknown_character(characters):
    data = [{"id": "definitely_not_a_character"}]

    error = validate_script_data(data, characters)

    assert error is not None
    assert "není v databázi" in error


def test_loader_accepts_script_with_meta(tmp_path, characters):
    path = tmp_path / "with_meta.json"
    _write_script(
        path,
        ["washerwoman", "butler", "poisoner", "imp"],
        meta=True,
    )

    script, error = script_loader(path, characters)

    assert error is None
    assert script.script_name == "Test Script"
    assert script.script_author == "pytest"


def test_loader_accepts_script_without_meta(tmp_path, characters):
    path = tmp_path / "without_meta.json"
    _write_script(
        path,
        ["washerwoman", "butler", "poisoner", "imp"],
        meta=False,
    )

    script, error = script_loader(path, characters)

    assert error is None
    assert script.script_name == "Without Meta"
    assert script.script_author is None


@pytest.mark.parametrize(
    ("character_id", "attribute"),
    [
        ("scapegoat", "travellers"),
        ("sentinel", "fabled"),
        ("stormcatcher", "loric"),
    ],
)
def test_loader_preserves_non_player_groups(
    tmp_path,
    characters,
    character_id,
    attribute,
):
    if character_id not in characters:
        pytest.skip(f"characters.json neobsahuje {character_id}.")

    path = tmp_path / f"{attribute}.json"
    _write_script(
        path,
        ["washerwoman", "butler", "poisoner", "imp", character_id],
        meta=True,
    )

    script, error = script_loader(path, characters)

    assert error is None
    loaded_ids = [character.character_id for character in getattr(script, attribute)]
    assert character_id in loaded_ids


def test_preloader_sorts_scripts_by_name(tmp_path, monkeypatch, characters):
    scripts_dir = tmp_path / "scripts"
    scripts_dir.mkdir()

    for filename, name in (
        ("zeta.json", "Zeta"),
        ("beta.json", "Beta"),
        ("alfa.json", "Alfa"),
    ):
        data = [
            {"id": "_meta", "name": name, "author": "pytest"},
            {"id": "washerwoman"},
        ]
        (scripts_dir / filename).write_text(
            json.dumps(data, ensure_ascii=False),
            encoding="utf-8",
        )

    monkeypatch.chdir(tmp_path)

    loaded = pre_loader()

    assert [item["script_name"] for item in loaded] == [
        "Alfa",
        "Beta",
        "Zeta",
    ]
