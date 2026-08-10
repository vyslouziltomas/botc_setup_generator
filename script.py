
class Script:
    def __init__(self, script):
        self.script_id = script["script_id"]
        self.script_name = script["script_name"]
        self.script_author = script["script_author"]
        self.townsfolk = script["townsfolk"]
        self.outsiders = script["outsiders"]
        self.minions = script["minions"]
        self.demons = script["demons"]

    def __str__(self):
        return self.script_name
    
    def validate(self, player_setup):
        if len(self.townsfolk) < player_setup.townsfolk:
            return "Script neobsahuje dostatek Townsfolk rolí."
        elif len(self.outsiders) < player_setup.outsiders:
            return "Script neobsahuje dostatek Outsider rolí."
        elif len(self.minions) < player_setup.minions:
            return "Script neobsahuje dostatek Minion rolí."
        elif len(self.demons) < player_setup.demons:
            return "Script neobsahuje dostatek Demon rolí."
        else:
            return None