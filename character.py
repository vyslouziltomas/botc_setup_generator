class Character:
        
    def __init__(self, data):
        self.character_id = data["character_id"]
        self.name_en = data["name_en"]
        self.name_cs = data["name_cs"]
        self.team = data["team"]
        self.setup_modifier = data["setup_modifier"]


    def __str__(self):
        return self.name_cs
