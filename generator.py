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
        
        # Používáme lokální proměnné místo přímé změny character.setup_modifier.
        # Objekty postav se totiž mohou znovu použít při dalších pokusech o generování.
        modifier_add = character.setup_modifier["add"]
        modifier_remove = character.setup_modifier["remove"]

        # Většina postav speciální setup modifier nemá.
        # .get() vrátí None, pokud klíč "special" ve slovníku neexistuje.
        special = character.setup_modifier.get("special")

        # Pokud má postava speciální setup modifier, zjistíme,
        # které z jeho možností lze v aktuálním setupu provést.
        if special:

            if special["type"] == "choice":
                available_options = []

                # Každou možnost speciálního modifieru posuzujeme samostatně.
                for option in special["options"]:
                    option_is_valid = True

                    # Ověříme, zda je ve scriptu dostatek postav,
                    # které lze podle této možnosti do setupu přidat.
                    for modifier_team, amount in option["add"].items():
                        available_characters = [
                            x
                            for x in getattr(script, modifier_team)
                            if x not in generated_teams[modifier_team]
                        ]

                        # Pokud není dostatek dostupných postav,
                        # tato možnost není proveditelná.
                        if amount > len(available_characters):
                            option_is_valid = False

                    # Ověříme, zda je v aktuálním setupu dostatek postav,
                    # které lze podle této možnosti odebrat.
                    for modifier_team, amount in option["remove"].items():
                        available_characters = [
                            x
                            for x in generated_teams[modifier_team]
                            if x not in modifier_characters
                        ]

                        # Postavy, které samy způsobily setup modifier,
                        # nepočítáme mezi postavy dostupné k odebrání.
                        if amount > len(available_characters):
                            option_is_valid = False

                    # Pokud prošly kontroly přidávání i odebírání,
                    # uložíme možnost mezi proveditelné varianty.
                    if option_is_valid:
                        available_options.append(option)

                # Pokud není proveditelná ani jedna možnost,
                # aktuální pokus o vygenerování setupu selhal.
                if not available_options:
                    generation_failed = True
                    return GeneratedSetup(
                        generated_teams,
                        generation_failed,
                        [],
                        [],
                        []
                    )

                # Z proveditelných možností náhodně vybereme jednu.
                selected_option = random.choice(available_options)

                # Vybranou variantu předáme dál standardnímu zpracování
                # add/remove modifierů.
                modifier_add = selected_option["add"]
                modifier_remove = selected_option["remove"]


            elif special["type"] == "conditional":

                # Conditional modifier má preferovanou variantu "if_true".
                # Tu použijeme pouze tehdy, pokud ji lze v aktuálním setupu
                # skutečně celou provést.
                true_option = special["if_true"]
                false_option = special["if_false"]

                true_option_is_valid = True

                # Nejprve zkontrolujeme, zda lze přidat všechny role,
                # které varianta "if_true" požaduje.
                for modifier_team, amount in true_option["add"].items():
                    available_characters = [
                        x
                        for x in getattr(script, modifier_team)
                        if x not in generated_teams[modifier_team]
                    ]

                    if amount > len(available_characters):
                        true_option_is_valid = False
                        break

                # Pokud je ADD část proveditelná, ověříme také REMOVE část.
                # Započítáváme pouze role, které nejsou chráněné tím,
                # že již aktivovaly vlastní setup modifier.
                if true_option_is_valid:
                    for modifier_team, amount in true_option["remove"].items():
                        available_characters = [
                            x
                            for x in generated_teams[modifier_team]
                            if x not in modifier_characters
                        ]

                        if amount > len(available_characters):
                            true_option_is_valid = False
                            break

                # Pokud lze preferovanou variantu provést, použijeme ji.
                # Jinak použijeme fallback variantu "if_false".
                if true_option_is_valid:
                    selected_option = true_option
                else:
                    selected_option = false_option

                # Vybranou variantu předáme standardnímu zpracování
                # ADD a REMOVE modifierů níže.
                modifier_add = selected_option["add"]
                modifier_remove = selected_option["remove"]


        # ADD modifier
        for modifier_team, amount in modifier_add.items():

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
        for modifier_team, amount in modifier_remove.items():

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