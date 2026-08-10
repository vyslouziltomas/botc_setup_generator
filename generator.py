import random
from generated_setup import GeneratedSetup


def generate_setup(script, player_setup):

    generation_failed = False
    modifier_characters = []
    message = []
    good_characters = script.townsfolk + script.outsiders

    generated_teams = {
        "townsfolk": [],
        "outsiders": [],
        "minions": [],
        "demons": []
    }

    generated_teams["townsfolk"].extend(
        random.sample(script.townsfolk, player_setup.townsfolk)
    )

    generated_teams["outsiders"].extend(
        random.sample(script.outsiders, player_setup.outsiders)
    )

    generated_teams["minions"].extend(
        random.sample(script.minions, player_setup.minions)
    )

    generated_teams["demons"].extend(
        random.sample(script.demons, player_setup.demons)
    )

    characters_to_process = (generated_teams["townsfolk"] + generated_teams["outsiders"] + generated_teams["minions"] + generated_teams["demons"])
    
    
#    print(
#        "ZÁKLAD:",
#        len(generated_teams["townsfolk"]),
#        len(generated_teams["outsiders"]),
#        len(generated_teams["minions"]),
#        len(generated_teams["demons"])
#        )
    

    while characters_to_process:

        character = characters_to_process.pop(0)

        for modifier_team, amount in character.setup_modifier["add"].items():
            if amount != 0 and character not in modifier_characters:
                modifier_characters.append(character)

            available_characters = [
                x
                for x in getattr(script, modifier_team)
                if x not in generated_teams[modifier_team]
            ]

            if amount > len(available_characters):

                generation_failed = True
                return GeneratedSetup(generated_teams, generation_failed, [], [])

            new_characters = random.sample(available_characters, amount)
            generated_teams[modifier_team].extend(new_characters)
            characters_to_process.extend(new_characters)


        for modifier_team, amount in character.setup_modifier["remove"].items():
            if amount != 0 and character not in modifier_characters:
                modifier_characters.append(character)

            available_characters = [
                x
                for x in generated_teams[modifier_team]
                if x not in modifier_characters
            ]

            if amount > len(available_characters):
                generation_failed = True
                return GeneratedSetup(generated_teams, generation_failed, [], [])

            characters_to_remove = random.sample(
                available_characters,
                amount
            )

            generated_teams[modifier_team] = [
                x
                for x in generated_teams[modifier_team]
                if x not in characters_to_remove
            ]

            characters_to_process = [
                x
                for x in characters_to_process
                if x not in characters_to_remove
            ]

#    print(
#        "PO MODIFIERECH:",
#        len(generated_teams["townsfolk"]),
#        len(generated_teams["outsiders"]),
#        len(generated_teams["minions"]),
#        len(generated_teams["demons"])
#    )


    generated_characters = [
        character
        for team in generated_teams.values()
        for character in team
    ]

    available_bluffs = [
        character
        for character in good_characters
        if character not in generated_characters and character.character_id != "drunk"
    ]

    drunk = next(
        (
            character
            for character in generated_characters
            if character.character_id == "drunk"
        ),
        None
    )

    if drunk:
        generated_characters.remove(drunk)
        generated_teams["outsiders"].remove(drunk)
        message.append("Jeden Měšťan je Opilec.")

    if len(available_bluffs) < 3:
        generation_failed = True
        return GeneratedSetup(generated_teams, generation_failed, [], [])
    
    bluffs = random.sample(available_bluffs, 3)


#    print(
#        "FINÁLNÍ:",
#        len(generated_teams["townsfolk"]),
#        len(generated_teams["outsiders"]),
#        len(generated_teams["minions"]),
#        len(generated_teams["demons"])
#        )

    return GeneratedSetup(generated_teams, generation_failed, bluffs, message)

