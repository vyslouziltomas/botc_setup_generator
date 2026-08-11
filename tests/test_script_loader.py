from character_loader import character_loader
from script_loader import script_loader

def test_script_loader():

    loaded_characters = character_loader()

    script = script_loader("scripts/trouble_brewing.json", loaded_characters)

    assert len(script.townsfolk) == 13
    assert len(script.outsiders) == 4
    assert len(script.minions) == 4
    assert len(script.demons) == 1