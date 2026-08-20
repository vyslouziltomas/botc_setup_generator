import importlib
import json
import random
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from character import Character


def _find_generator_module():
    """Najde modul projektu, který obsahuje funkci generate_setup()."""
    preferred = (
        "generator",
        "setup_generator",
        "setup",
        "generation",
    )

    for module_name in preferred:
        try:
            module = importlib.import_module(module_name)
        except ModuleNotFoundError:
            continue

        if hasattr(module, "generate_setup"):
            return module

    for path in PROJECT_ROOT.glob("*.py"):
        if path.stem.startswith("test_") or path.stem in {"conftest"}:
            continue

        try:
            source = path.read_text(encoding="utf-8")
        except OSError:
            continue

        if "def generate_setup(" not in source:
            continue

        module = importlib.import_module(path.stem)
        if hasattr(module, "generate_setup"):
            return module

    raise RuntimeError(
        "Nepodařilo se najít modul s generate_setup(). "
        "Přejmenuj modul na generator.py/setup_generator.py, "
        "nebo doplň jeho název do tests/conftest.py."
    )


GENERATOR_MODULE = _find_generator_module()
generate_setup = GENERATOR_MODULE.generate_setup


@pytest.fixture(scope="session")
def characters():
    path = PROJECT_ROOT / "characters.json"
    data = json.loads(path.read_text(encoding="utf-8"))

    result = {}
    for item in data:
        character = Character(item)
        result[character.character_id] = character

    return result


def empty_modifier(character):
    modifier = character.setup_modifier
    return (
        not modifier.get("add")
        and not modifier.get("remove")
        and not modifier.get("special")
    )


def safe_characters(characters, team, *, exclude=()):
    excluded = set(exclude)
    return [
        character
        for character in characters.values()
        if character.team == team
        and character.character_id not in excluded
        and empty_modifier(character)
        and character.character_id not in {"lunatic", "drunk"}
    ]


def make_script(
    characters,
    *,
    townsfolk=(),
    outsiders=(),
    minions=(),
    demons=(),
    extra_townsfolk=0,
    extra_outsiders=0,
    extra_minions=0,
    extra_demons=0,
):
    """Vytvoří lehký Script objekt vhodný pro jednotkové testy."""
    used = set(townsfolk) | set(outsiders) | set(minions) | set(demons)

    def resolve(ids):
        return [characters[character_id] for character_id in ids]

    def extras(team, amount):
        pool = safe_characters(characters, team, exclude=used)
        if len(pool) < amount:
            raise AssertionError(
                f"Pro test není v characters.json dost bezpečných rolí týmu {team}."
            )
        chosen = pool[:amount]
        used.update(character.character_id for character in chosen)
        return chosen

    return SimpleNamespace(
        townsfolk=resolve(townsfolk) + extras("townsfolk", extra_townsfolk),
        outsiders=resolve(outsiders) + extras("outsiders", extra_outsiders),
        minions=resolve(minions) + extras("minions", extra_minions),
        demons=resolve(demons) + extras("demons", extra_demons),
        travellers=[],
        fabled=[],
        loric=[],
    )


def player_setup(townsfolk, outsiders, minions, demons):
    return SimpleNamespace(
        townsfolk=townsfolk,
        outsiders=outsiders,
        minions=minions,
        demons=demons,
    )


def result_teams(result):
    if hasattr(result, "generated_teams"):
        return result.generated_teams
    if hasattr(result, "teams"):
        return result.teams
    raise AssertionError("GeneratedSetup nemá atribut generated_teams ani teams.")


def result_failed(result):
    if hasattr(result, "generation_failed"):
        return result.generation_failed
    if hasattr(result, "failed"):
        return result.failed
    raise AssertionError("GeneratedSetup nemá atribut generation_failed ani failed.")


def result_bluffs(result):
    return getattr(result, "bluffs", [])


def result_messages(result):
    if hasattr(result, "message"):
        return result.message
    if hasattr(result, "messages"):
        return result.messages
    return []


def flatten(teams):
    return [
        character
        for team in teams.values()
        for character in team
    ]


def ids(characters):
    return [character.character_id for character in characters]


def generate_success(script, setup, attempts=100):
    """
    Generátor může legitimně některý náhodný pokus zahodit.
    Pro test hledáme první úspěšný deterministický seed.
    """
    for seed in range(attempts):
        random.seed(seed)
        result = generate_setup(script, setup)
        if not result_failed(result):
            return result

    pytest.fail(f"Nepodařilo se vygenerovat platný setup ani po {attempts} seed pokusech.")
