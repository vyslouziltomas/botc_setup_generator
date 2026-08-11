from character_loader import character_loader

def test_character_loader():

    loaded_characters = character_loader()
    assert "empath" in loaded_characters
    assert loaded_characters["empath"].name_cs == "Empat"