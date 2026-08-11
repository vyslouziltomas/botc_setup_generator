from player_count_loader import player_count_loader, get_player_count_setup

def test_player_count_loader():
    player_setups = player_count_loader()
    player_setup = get_player_count_setup(player_setups, 8)

    assert player_setup.townsfolk == 5
    assert player_setup.outsiders == 1
    assert player_setup.minions == 1
    assert player_setup.demons == 1

def test_invalid_player_count():
    player_setups = player_count_loader()
    player_setup = get_player_count_setup(player_setups, 3)

    assert player_setup is None