import random
from generated_setup import GeneratedSetup


def generate_setup(script, player_setup):

    generation_failed = False

    # Role, jejichž setup modifier už byl aktivován.
    # Chráníme je před pozdějším odstraněním, aby se nerozbila
    # již aplikovaná posloupnost modifierů.
    modifier_characters = []

    message = []

    # Bluffy mohou být pouze dobré role ze scriptu.
    good_characters = script.townsfolk + script.outsiders

    generated_teams = {
        "townsfolk": [],
        "outsiders": [],
        "minions": [],
        "demons": []
    }

    # Základní setup podle počtu hráčů, zatím bez zohlednění modifierů.
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

    # Fronta rolí, jejichž setup modifier ještě nebyl zpracován.
    # Nově přidané role se do fronty přidávají také, protože mohou
    # mít vlastní modifier.
    characters_to_process = (
        generated_teams["townsfolk"]
        + generated_teams["outsiders"]
        + generated_teams["minions"]
        + generated_teams["demons"]
    )

    # Modifiery se zpracovávají postupně, dokud nezůstanou žádné
    # nové role čekající na kontrolu.
    while characters_to_process:

        character = characters_to_process.pop(0)

        # ADD modifier
        for modifier_team, amount in character.setup_modifier["add"].items():

            if amount != 0 and character not in modifier_characters:
                modifier_characters.append(character)

            # Přidávat lze pouze role, které ještě nejsou v setupu.
            available_characters = [
                x
                for x in getattr(script, modifier_team)
                if x not in generated_teams[modifier_team]
            ]

            # Pokud modifier nelze splnit, celý pokus o generování se zahodí.
            if amount > len(available_characters):
                generation_failed = True
                return GeneratedSetup(
                    generated_teams,
                    generation_failed,
                    [],
                    [],
                    []
                )

            new_characters = random.sample(
                available_characters,
                amount
            )

            generated_teams[modifier_team].extend(new_characters)

            # Nové role musí být také zkontrolovány kvůli případným
            # vlastním setup modifierům.
            characters_to_process.extend(new_characters)

        # REMOVE modifier
        for modifier_team, amount in character.setup_modifier["remove"].items():

            if amount != 0 and character not in modifier_characters:
                modifier_characters.append(character)

            # Již aktivované modifier role nesmějí být odstraněny.
            available_characters = [
                x
                for x in generated_teams[modifier_team]
                if x not in modifier_characters
            ]

            if amount > len(available_characters):
                generation_failed = True
                return GeneratedSetup(
                    generated_teams,
                    generation_failed,
                    [],
                    [],
                    []
                )

            characters_to_remove = random.sample(
                available_characters,
                amount
            )

            generated_teams[modifier_team] = [
                x
                for x in generated_teams[modifier_team]
                if x not in characters_to_remove
            ]

            # Odebraná role nesmí později aktivovat svůj modifier,
            # pokud ještě čekala ve frontě.
            characters_to_process = [
                x
                for x in characters_to_process
                if x not in characters_to_remove
            ]

    # Po dokončení modifierů vytvoříme plochý seznam všech rolí
    # pro kontrolu bluffů a speciálních pravidel.
    generated_characters = [
        character
        for team in generated_teams.values()
        for character in team
    ]

    # Bluff nesmí být ve hře a Opilec nemůže být bluff nikdy.
    available_bluffs = [
        character
        for character in good_characters
        if character not in generated_characters
        and character.character_id != "drunk"
    ]

    drunk = next(
        (
            character
            for character in generated_characters
            if character.character_id == "drunk"
        ),
        None
    )

    # Opilec se během generování musí počítat jako Outsider,
    # aby se aplikoval jeho modifier. Ve výsledku se ale nezobrazuje,
    # protože vypravěč použije místo jeho tokenu jednu Townsfolk roli.
    if drunk:
        generated_characters.remove(drunk)
        generated_teams["outsiders"].remove(drunk)
        message.append("Jeden měšťan je Opilec.")

    # Demon musí mít vždy tři platné bluffy.
    if len(available_bluffs) < 3:
        generation_failed = True
        return GeneratedSetup(
            generated_teams,
            generation_failed,
            [],
            [],
            []
        )

    bluffs = random.sample(available_bluffs, 3)

    return GeneratedSetup(
        generated_teams,
        generation_failed,
        bluffs,
        message,
        generated_characters
    )