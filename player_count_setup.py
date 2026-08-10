class PlayerCountSetup:

    def __init__(self, setup):
        self.player_count = setup["player_count"]
        self.townsfolk = setup["teams"]["townsfolk"]
        self.outsiders = setup["teams"]["outsiders"]
        self.minions = setup["teams"]["minions"]
        self.demons = setup["teams"]["demons"]

    def __str__(self):
        return f"{self.player_count} hráčů: {self.townsfolk} Townsfolk, {self.outsiders} Outsiders, {self.minions} Minions, {self.demons} Demon"