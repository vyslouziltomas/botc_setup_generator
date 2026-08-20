import random
from generated_setup import GeneratedSetup


def generate_setup(script, player_setup):

    generation_failed = False

    generated_teams = {
        "townsfolk": [],
        "outsiders": [],
        "minions": [],
        "demons": []
    }

    message = []
    no_bluffs = False
    no_evil = False
    xaan_outsiders_count = None
    xaan_correction_count = 0

    # ----- Základní setup podle počtu hráčů -----

    # Script musí obsahovat dostatek rolí pro základní setup.
    if (
        len(script.townsfolk) < player_setup.townsfolk
        or len(script.outsiders) < player_setup.outsiders
        or len(script.minions) < player_setup.minions
        or len(script.demons) < player_setup.demons
    ):
        return GeneratedSetup(
            generated_teams,
            True,
            [],
            [],
            []
        )

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

    # ----- Fronta a modifikátory setupu -----

    # Fronta rolí, jejichž setup modifier ještě nebyl zpracován.
    # Nově přidané role se do fronty přidávají také, protože mohou
    # mít vlastní modifier.
    characters_to_process = (
        generated_teams["townsfolk"]
        + generated_teams["outsiders"]
        + generated_teams["minions"]
        + generated_teams["demons"]
    )

    # Kazali / Lord of Typhon / Legion, pokud je přítomný, musí svůj setup modifier zpracovat
    # jako první, protože kompletně mění běžné složení setupu.
    for character_to_process in characters_to_process:

        if character_to_process.character_id in ("kazali", "lordoftyphon", "legion"):
            characters_to_process.remove(character_to_process)
            characters_to_process.insert(0, character_to_process)
            break

    # Role, jejichž setup modifier už byl aktivován.
    # Chráníme je před pozdějším odstraněním, aby se nerozbila
    # již aplikovaná posloupnost modifierů.
    modifier_characters = []

    # Role přidané jinou rolí, které musí zůstat v setupu,
    # dokud je přítomná role, která je přidala.
    protected_characters = {}

    # Role, které se do setupu nemohou dostat na základě schopnosti jiné role.
    excluded_characters = []

    # Modifiery se zpracovávají postupně, dokud nezůstanou žádné
    # nové role čekající na kontrolu.
    # To celé se ještě kontroluje kvůli Xaanovi (může přidávat do fronty i po jejím vyprázdnění).
    while True:

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
                                if generated_teams[modifier_team].count(x) < x.max_in_play
                                and x not in excluded_characters
                            ]

                            # Pokud není dostatek dostupných postav,
                            # tato možnost není proveditelná.
                            if amount > len(available_characters):
                                option_is_valid = False

                        # Ověříme, zda je v aktuálním setupu dostatek postav,
                        # které lze podle této možnosti odebrat. Hlídáme chráněné role.
                        for modifier_team, amount in option["remove"].items():

                            available_characters = [
                                x
                                for x in generated_teams[modifier_team]
                                if (
                                    x not in modifier_characters
                                    or (
                                        x is character
                                        # Hermit může odstranit sám sebe
                                        and special.get("self_removal_allowed", False)
                                    )
                                )
                                and not any(
                                    protector in team
                                    for protector in protected_characters.get(x, [])
                                    for team in generated_teams.values()
                                )
                            ]

                            # Postavy, které samy způsobily setup modifier,
                            # nepočítáme mezi postavy dostupné k odebrání.
                            if amount > len(available_characters):
                                option_is_valid = False

                        # Pokud prošly kontroly přidávání i odebírání,
                        # uložíme variantu mezi proveditelné varianty.
                        if option_is_valid:
                            available_options.append(option)

                    # Pokud není proveditelná ani jedna varianta,
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

                    # Z proveditelných variant náhodně vybereme jednu.
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
                            if generated_teams[modifier_team].count(x) < x.max_in_play
                            and x not in excluded_characters
                        ]

                        if amount > len(available_characters):
                            true_option_is_valid = False
                            break

                    # Pokud je ADD část proveditelná, ověříme také REMOVE část.
                    # Započítáváme pouze role, které nejsou chráněné tím,
                    # že již aktivovaly vlastní setup modifier, či chráněné jinou rolí.
                    if true_option_is_valid:

                        for modifier_team, amount in true_option["remove"].items():

                            available_characters = [
                                x
                                for x in generated_teams[modifier_team]
                                if x not in modifier_characters
                                and not any(
                                    protector in team
                                    for protector in protected_characters.get(x, [])
                                    for team in generated_teams.values()
                                )
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

                elif special["type"] == "duplicate_self":

                    # Náhodně určíme počet dalších kopií role.
                    duplicates_to_add = random.choice(special["options"])

                    current_count = generated_teams[character.team].count(character)

                    # Celkový počet kopií nesmí překročit limit dané role.
                    if current_count + duplicates_to_add > character.max_in_play:
                        generation_failed = True
                        return GeneratedSetup(
                            generated_teams,
                            generation_failed,
                            [],
                            [],
                            []
                        )

                    # Kopie nahrazuje jiné Townsfolk role.
                    # Samotné kopie ani již aktivované modifier role
                    # nesmíme vybrat k odebrání. Hlídáme chráněné role.
                    available_characters = [
                        x
                        for x in generated_teams["townsfolk"]
                        if x is not character
                        and x not in modifier_characters
                        and not any(
                            protector in team
                            for protector in protected_characters.get(x, [])
                            for team in generated_teams.values()
                        )
                    ]

                    if duplicates_to_add > len(available_characters):
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
                        duplicates_to_add
                    )

                    # Každou nahrazovanou roli odebíráme jednotlivě.
                    # .remove() odstraní pouze jeden výskyt, takže tato logika
                    # zůstává bezpečná i pro role, které mohou být v setupu vícekrát.
                    for character_to_remove in characters_to_remove:
                        generated_teams["townsfolk"].remove(character_to_remove)

                        # Pokud odebraná role ještě čekala na zpracování svého modifieru,
                        # odstraníme ji také z fronty.
                        if character_to_remove in characters_to_process:
                            characters_to_process.remove(character_to_remove)

                    # Přidané kopie nedáváme do characters_to_process.
                    # Jde stále o stejnou roli a její duplicate_self modifier
                    # se má během generování aktivovat pouze jednou.
                    for _ in range(duplicates_to_add):
                        generated_teams[character.team].append(character)

                    # Původce modifieru se označí jako aktivovaný.
                    if character not in modifier_characters:
                        modifier_characters.append(character)

                elif special["type"] == "add_specific_character":

                    specific_character_id = special["character_id"]

                    # Konkrétní přidávaná role může patřit do kteréhokoli týmu,
                    # proto ji hledáme mezi všemi rolemi dostupnými na scriptu.
                    script_characters = script.townsfolk + script.outsiders + script.minions + script.demons

                    specific_character = next(
                        (
                            x
                            for x in script_characters
                            if x.character_id == specific_character_id
                        ),
                        None
                    )

                    # Pokud požadovaná role na scriptu vůbec není, tento setup modifier nelze splnit.
                    # Pokud je mezi vyloučenými rolemi, taktéž se jedná o neplatný setup.
                    if specific_character is None or specific_character in excluded_characters:
                        generation_failed = True
                        return GeneratedSetup(
                            generated_teams,
                            generation_failed,
                            [],
                            [],
                            []
                        )

                    specific_character_is_in_setup = any(
                        specific_character in team
                        for team in generated_teams.values()
                    )

                    # Pokud už konkrétní role ve hře je, není potřeba setup měnit.
                    if not specific_character_is_in_setup:

                        for modifier_team, amount in special["remove"].items():

                            # Nahrazovaná role nesmí být samotný původce modifieru,
                            # již aktivovaná modifier role ani role chráněná jinou
                            # stále přítomnou postavou.
                            available_characters = [
                                x
                                for x in generated_teams[modifier_team]
                                if x is not character
                                and x not in modifier_characters
                                and not any(
                                    protector in team
                                    for protector in protected_characters.get(x, [])
                                    for team in generated_teams.values()
                                )
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

                            characters_to_remove = random.sample(available_characters, amount)

                            # Nahrazené role odebereme také z fronty modifierů,
                            # pokud ještě čekaly na zpracování.
                            for character_to_remove in characters_to_remove:
                                generated_teams[modifier_team].remove(character_to_remove)

                                if character_to_remove in characters_to_process:
                                    characters_to_process.remove(character_to_remove)

                        # Konkrétní role může mít vlastní setup modifier,
                        # proto ji přidáme také do fronty ke zpracování.
                        generated_teams[specific_character.team].append(specific_character)
                        characters_to_process.append(specific_character)

                    # Ať byla role přidána nyní, nebo už v setupu byla,
                    # musí zůstat chráněná, dokud je přítomný původce modifieru.
                    protected_characters.setdefault(specific_character, []).append(character)

                    # Tento special provedl potřebné změny sám,
                    # standardní ADD/REMOVE už se proto nemají aplikovat.
                    # Původce modifieru se označí jako aktivovaný.
                    if character not in modifier_characters:
                        modifier_characters.append(character)

                    modifier_add = {}
                    modifier_remove = {}

                elif special["type"] == "remove_self":

                    # Role aktivuje svůj setup modifier, ale sama
                    # ve výsledném hráčském setupu nezůstává.
                    generated_teams[character.team].remove(character)

                    if character.character_id == "drunk":
                        message.append("Jeden měšťan je ve skutečnosti Opilec.")

                    elif character.character_id == "lilmonsta":                    
                        message.append("Přisluhovači každou noc rozhodnou, kdo hlídá Lil' Monstu.")
                        no_bluffs = True

                    elif character.character_id == "marionette":
                        message.append("Jeden dobrý hráč sousedící s démonem je ve skutečnosti Marioneta.")

                elif special["type"] == "copy_good_ability":

                    # Boffin může dát Démonovi schopnost dobré role, která není ve hře.
                    # Některé role jsou kvůli jinx pravidlům z výběru úplně vyloučené.
                    forbidden_boffin_abilities = ("drunk", "heretic", "ogre", "politician", "atheist")

                    available_boffin_abilities = [
                        x
                        for x in script.townsfolk + script.outsiders
                        if x.character_id not in forbidden_boffin_abilities
                        and x not in excluded_characters
                        and not any(
                            x in team
                            for team in generated_teams.values()
                        )
                    ]

                    if not available_boffin_abilities:
                        generation_failed = True
                        return GeneratedSetup(
                            generated_teams,
                            generation_failed,
                            [],
                            [],
                            []
                        )

                    # Zvolíme Boffin schopnost a zakážeme jí pro další výběry. 
                    boffin_ability = random.choice(available_boffin_abilities)
                    excluded_characters.append(boffin_ability)

                    # Boffina chráníme před pozdějším odstraněním.
                    if character not in modifier_characters:
                        modifier_characters.append(character)

                    boffin_special = boffin_ability.setup_modifier.get("special")

                    if boffin_ability.character_id == "villageidiot":
                        # Nespustí se modifier (jinx pravidlo).
                        pass

                    elif boffin_special:

                        if boffin_special["type"] == "choice":

                            available_options = []

                            # Ověříme proveditelnost každé varianty modifieru.
                            for option in boffin_special["options"]:
                                option_is_valid = True

                                # Kontrola rolí, které varianta přidává.
                                for modifier_team, amount in option["add"].items():

                                    available_characters = [
                                        x
                                        for x in getattr(script, modifier_team)
                                        if generated_teams[modifier_team].count(x) < x.max_in_play
                                        and x not in excluded_characters
                                    ]

                                    if amount > len(available_characters):
                                        option_is_valid = False

                                # Kontrola rolí, které varianta odebírá.
                                # Již aktivované a chráněné role odebrat nelze.
                                for modifier_team, amount in option["remove"].items():

                                    available_characters = [
                                        x
                                        for x in generated_teams[modifier_team]
                                        if x not in modifier_characters
                                        and not any(
                                            protector in team
                                            for protector in protected_characters.get(x, [])
                                            for team in generated_teams.values()
                                        )
                                    ]

                                    if amount > len(available_characters):
                                        option_is_valid = False

                                if option_is_valid:
                                    available_options.append(option)

                            # Pokud nelze provést žádnou variantu, setup zahodíme.
                            if not available_options:
                                generation_failed = True
                                return GeneratedSetup(
                                    generated_teams,
                                    generation_failed,
                                    [],
                                    [],
                                    []
                                )

                            # Z proveditelných variant jednu náhodně vybereme.
                            selected_option = random.choice(available_options)

                            # Vybranou variantu zpracuje společná ADD/REMOVE logika.
                            modifier_add = selected_option["add"]
                            modifier_remove = selected_option["remove"]

                        elif boffin_special["type"] == "conditional":

                            true_option = boffin_special["if_true"]
                            false_option = boffin_special["if_false"]

                            true_option_is_valid = True

                            # Ověříme, zda lze provést ADD část preferované varianty.
                            for modifier_team, amount in true_option["add"].items():

                                available_characters = [
                                    x
                                    for x in getattr(script, modifier_team)
                                    if generated_teams[modifier_team].count(x) < x.max_in_play
                                    and x not in excluded_characters
                                ]

                                if amount > len(available_characters):
                                    true_option_is_valid = False
                                    break

                            # Pokud je ADD část proveditelná, ověříme také REMOVE.
                            if true_option_is_valid:

                                for modifier_team, amount in true_option["remove"].items():

                                    available_characters = [
                                        x
                                        for x in generated_teams[modifier_team]
                                        if x not in modifier_characters
                                        and not any(
                                            protector in team
                                            for protector in protected_characters.get(x, [])
                                            for team in generated_teams.values()
                                        )
                                    ]

                                    if amount > len(available_characters):
                                        true_option_is_valid = False
                                        break

                            # Preferujeme if_true; pokud ji nelze provést,
                            # použijeme fallback variantu.
                            if true_option_is_valid:
                                selected_option = true_option
                            else:
                                selected_option = false_option

                            modifier_add = selected_option["add"]
                            modifier_remove = selected_option["remove"]
                        
                        elif boffin_special["type"] == "add_specific_character":

                            specific_character_id = boffin_special["character_id"]

                            script_characters = (
                                script.townsfolk
                                + script.outsiders
                                + script.minions
                                + script.demons
                            )

                            specific_character = next(
                                (
                                    x
                                    for x in script_characters
                                    if x.character_id == specific_character_id
                                ),
                                None
                            )

                            # Požadovaná role musí být na scriptu a nesmí být
                            # vyloučena jinou setup schopností.
                            if (
                                specific_character is None
                                or specific_character in excluded_characters
                            ):
                                generation_failed = True
                                return GeneratedSetup(
                                    generated_teams,
                                    generation_failed,
                                    [],
                                    [],
                                    []
                                )

                            specific_character_is_in_setup = any(
                                specific_character in team
                                for team in generated_teams.values()
                            )

                            # Pokud už konkrétní role ve hře je, setup se nemění.
                            if not specific_character_is_in_setup:

                                for modifier_team, amount in boffin_special["remove"].items():

                                    available_characters = [
                                        x
                                        for x in generated_teams[modifier_team]
                                        if x is not character
                                        and x not in modifier_characters
                                        and not any(
                                            protector in team
                                            for protector in protected_characters.get(x, [])
                                            for team in generated_teams.values()
                                        )
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

                                    characters_to_remove = random.sample(available_characters, amount)

                                    for character_to_remove in characters_to_remove:

                                        generated_teams[modifier_team].remove(
                                            character_to_remove
                                        )

                                        if character_to_remove in characters_to_process:
                                            characters_to_process.remove(
                                                character_to_remove
                                            )

                                generated_teams[specific_character.team].append(
                                    specific_character
                                )

                                characters_to_process.append(
                                    specific_character
                                )

                            # Konkrétní role vzniká kvůli Boffinově schopnosti,
                            # proto ji chráníme, dokud je Boffin v setupu.
                            protected_characters.setdefault(
                                specific_character,
                                []
                            ).append(character)

                            modifier_add = {}
                            modifier_remove = {}

                        else:
                            generation_failed = True
                            return GeneratedSetup(
                                generated_teams,
                                generation_failed,
                                [],
                                [],
                                []
                            )
                        
                    else:
                        # Jednoduchý ADD/REMOVE modifier můžeme použít přímo.
                        modifier_add = boffin_ability.setup_modifier["add"]
                        modifier_remove = boffin_ability.setup_modifier["remove"]

                    message.append(f"Boffin dává démonovi schopnost role {boffin_ability.name_cs}.")

                elif special["type"] == "legion":

                    # Legie nahrazují běžné rozložení týmů.
                    generated_teams = {
                        "townsfolk": [],
                        "outsiders": [],
                        "minions": [],
                        "demons": []
                    }

                    # Zahodíme stav původního setupu.
                    characters_to_process.clear()
                    modifier_characters.clear()
                    protected_characters.clear()
                    excluded_characters.clear()
                    message.clear()
                    no_bluffs = False
                    no_evil = False
                    xaan_outsiders_count = None
                    xaan_correction_count = 0

                    # Obrátíme běžný poměr good/evil.
                    total_players = (
                        player_setup.townsfolk
                        + player_setup.outsiders
                        + player_setup.minions
                        + player_setup.demons
                    )

                    legion_good_count = (
                        player_setup.minions
                        + player_setup.demons
                    )

                    # Ve hře s Legiemi musí být alespoň dva good hráči.
                    legion_good_count = max(
                        legion_good_count,
                        2
                    )

                    legion_count = (
                        total_players - legion_good_count
                    )

                    # Legie musí tvořit většinu a nepřekročit max_in_play.
                    if (
                        legion_count <= legion_good_count
                        or legion_count > character.max_in_play
                    ):
                        generation_failed = True
                        return GeneratedSetup(
                            generated_teams,
                            generation_failed,
                            [],
                            [],
                            []
                        )

                    # Vyřadíme role přidávající evil postavy a Atheistu.
                    available_good_characters = [
                        x
                        for x in script.townsfolk + script.outsiders
                        if x.setup_modifier["add"].get("minions", 0) == 0
                        and x.setup_modifier["add"].get("demons", 0) == 0
                        and x.setup_modifier.get("special", {}).get("type") != "no_evil"
                    ]

                    available_townsfolk = [
                        x
                        for x in available_good_characters
                        if x.team == "townsfolk"
                    ]

                    available_outsiders = [
                        x
                        for x in available_good_characters
                        if x.team == "outsiders"
                    ]

                    # Preferujeme 0–1 Outsidera, maximálně povolíme dva.
                    available_outsider_counts = [
                        outsider_count
                        for outsider_count in range(
                            min(2, legion_good_count) + 1
                        )
                        if outsider_count <= len(available_outsiders)
                        and legion_good_count - outsider_count <= len(available_townsfolk)
                    ]

                    if not available_outsider_counts:
                        generation_failed = True
                        return GeneratedSetup(
                            generated_teams,
                            generation_failed,
                            [],
                            [],
                            []
                        )

                    outsider_count_weights = [
                        {
                            0: 4,
                            1: 2,
                            2: 1
                        }[outsider_count]
                        for outsider_count in available_outsider_counts
                    ]

                    legion_outsiders_count = random.choices(
                        available_outsider_counts,
                        weights=outsider_count_weights,
                        k=1
                    )[0]

                    legion_townsfolk_count = (
                        legion_good_count - legion_outsiders_count
                    )

                    # Vylosujeme konkrétní good role.
                    regenerated_townsfolk = random.sample(
                        available_townsfolk,
                        legion_townsfolk_count
                    )

                    regenerated_outsiders = random.sample(
                        available_outsiders,
                        legion_outsiders_count
                    )

                    generated_teams["townsfolk"].extend(
                        regenerated_townsfolk
                    )

                    generated_teams["outsiders"].extend(
                        regenerated_outsiders
                    )

                    # Přidáme potřebný počet Legií.
                    for _ in range(legion_count):
                        generated_teams["demons"].append(character)

                    modifier_characters.append(character)

                    # Good role ještě musí zpracovat vlastní modifiery.
                    characters_to_process.extend(
                        regenerated_townsfolk + regenerated_outsiders
                    )

                    message.append(f"Ve hře je {legion_count} Legií a {legion_good_count} dobří hráči.")
                    message.append("Během první noci se všechny Legie navzájem poznají.")
                    message.append("Všechny Legie dostanou 0 - 3 stejné bluffy.")

                    modifier_add = {}
                    modifier_remove = {}
         
                elif special["type"] == "no_minions":

                    # Kazali / Lord of Typhon má při setupu přednost před již vygenerovanými rolemi.
                    # Zahodíme tedy celý dosavadní setup i stav jeho modifierů
                    # a ponecháme pouze samotného Kazaliho  / Lorda of Typhon.
                    generated_teams = {
                        "townsfolk": [],
                        "outsiders": [],
                        "minions": [],
                        "demons": [character]
                    }

                    characters_to_process.clear()
                    modifier_characters.clear()
                    protected_characters.clear()
                    excluded_characters.clear()
                    message.clear()
                    no_bluffs = False
                    no_evil = False
                    xaan_outsiders_count = None
                    xaan_correction_count = 0

                    # Kazali / Lord of Typhon musí po aktivaci svého setup modifieru zůstat ve hře,
                    # jinak by se rozbil smysl celé regenerace.
                    modifier_characters.append(character)

                    # Z poolu dobrých rolí vyřadíme role, které běžným modifierem
                    # přidávají Miniona nebo Démona. Atheistu také nepovolíme,
                    # protože jeho setup je s Kazalim / Lordem of Typhon v rozporu.
                    available_good_characters = [
                        x
                        for x in script.townsfolk + script.outsiders
                        if x.setup_modifier["add"].get("minions", 0) == 0
                        and x.setup_modifier["add"].get("demons", 0) == 0
                        and x.setup_modifier.get("special", {}).get("type") != "no_evil"
                        and x not in excluded_characters
                    ]

                    # Role rozdělíme podle týmu, protože nejdřív určujeme výsledný
                    # počet Outsiderů a teprve potom vybíráme konkrétní postavy.
                    available_townsfolk = [
                        x
                        for x in available_good_characters
                        if x.team == "townsfolk"
                    ]
                    available_outsiders = [
                        x
                        for x in available_good_characters
                        if x.team == "outsiders"
                    ]

                    # Minion sloty se v Kazali / Lord of Typhon setupu také zaplní dobrými rolemi.
                    # Celkový počet hráčů tak zůstane stejný.
                    good_slots = (player_setup.townsfolk + player_setup.outsiders + player_setup.minions)

                    # Připravíme pouze takové počty Outsiderů, které lze skutečně
                    # sestavit z dostupných rolí na scriptu.
                    available_outsider_counts = [
                        outsider_count
                        for outsider_count in range(len(available_outsiders) + 1)
                        if outsider_count <= good_slots
                        and good_slots - outsider_count <= len(available_townsfolk)
                    ]

                    if not available_outsider_counts:
                        generation_failed = True
                        return GeneratedSetup(
                            generated_teams,
                            generation_failed,
                            [],
                            [],
                            []
                        )

                    # Kazali / Lord of Typhon může počet Outsiderů výrazně změnit, ale
                    # běžný počet podle player setupu preferujeme. Čím dál je varianta
                    # od standardu, tím menší váhu při náhodném výběru dostane.
                    outsider_count_weights = []

                    for outsider_count in available_outsider_counts:

                        difference = abs(
                            outsider_count - player_setup.outsiders
                        )

                        if difference == 0:
                            weight = 4

                        elif difference == 1:
                            weight = 2

                        else:
                            weight = 1

                        outsider_count_weights.append(weight)

                    no_minions_outsiders_count = random.choices(
                        available_outsider_counts,
                        weights=outsider_count_weights,
                        k=1
                    )[0]

                    no_minions_townsfolk_count = (good_slots - no_minions_outsiders_count)

                    # Počet rolí už máme určený, nyní náhodně vybereme
                    # konkrétní Townsfolk a Outsidery.
                    regenerated_townsfolk = random.sample(
                        available_townsfolk,
                        no_minions_townsfolk_count
                    )

                    regenerated_outsiders = random.sample(
                        available_outsiders,
                        no_minions_outsiders_count
                    )

                    generated_teams["townsfolk"].extend(
                        regenerated_townsfolk
                    )

                    generated_teams["outsiders"].extend(
                        regenerated_outsiders
                    )

                    # Nově vygenerované dobré role musí projít standardním
                    # zpracováním, protože mohou mít vlastní setup modifiery.
                    characters_to_process.extend(regenerated_townsfolk + regenerated_outsiders)

                    if character.character_id == "kazali":
                        message.append("Kazali během první noci vybere hráče, kteří se stanou zlými přisluhovači.")

                    elif character.character_id == "lordoftyphon":
                        message.append(f"Během první noci se {player_setup.minions  + 1} sousedé démona stanou zlými přisluhovači.")

                    # Závěrečná pojistka: samotný Kazali / Lord of Typhon setup nesmí
                    # v této fázi obsahovat žádné Miniony.
                    if generated_teams["minions"]:
                        generation_failed = True
                        return GeneratedSetup(
                            generated_teams,
                            generation_failed,
                            [],
                            [],
                            []
                        )

                elif special["type"] == "no_demon":

                    # Pokud už některý Démon aktivoval svůj setup modifier,
                    # jeho změny bychom po odstranění nedokázali bezpečně vrátit.
                    # Takový pokus proto zahodíme a generování proběhne znovu.
                    demon_modifier_activated = any(
                        demon in modifier_characters
                        for demon in generated_teams["demons"]
                    )

                    if demon_modifier_activated:
                        generation_failed = True
                        return GeneratedSetup(
                            generated_teams,
                            generation_failed,
                            [],
                            [],
                            []
                        )

                    # Démoni se při základním setupu vybírají standardně,
                    # ale tato role vyžaduje setup bez Démona.
                    demons_to_remove = generated_teams["demons"].copy()

                    for demon in demons_to_remove:
                        generated_teams["demons"].remove(demon)

                        # Odebraný Démon nesmí později aktivovat svůj modifier,
                        # pokud ještě čekal ve frontě.
                        if demon in characters_to_process:
                            characters_to_process.remove(demon)

                    if character not in modifier_characters:
                        modifier_characters.append(character)
                    
                    if character.character_id == "summoner":                    
                        message.append("Ve hře není démon. Vyvolávač dostane 3 blafy.")

                elif special["type"] == "no_evil":

                    no_evil = True
                    no_bluffs = True

                    evil_characters = (
                        generated_teams["minions"]
                        + generated_teams["demons"]
                    )

                    # Pokud už některá zlá role aktivovala svůj setup modifier,
                    # její změny bychom nedokázali bezpečně vrátit.
                    evil_modifier_activated = any(
                        evil_character in modifier_characters
                        for evil_character in evil_characters
                    )

                    if evil_modifier_activated:
                        generation_failed = True
                        return GeneratedSetup(
                            generated_teams,
                            generation_failed,
                            [],
                            [],
                            []
                        )

                    evil_count = len(evil_characters)

                    # Odstraněné zlé role nesmějí později aktivovat své modifiery.
                    for evil_character in evil_characters:
                        if evil_character in characters_to_process:
                            characters_to_process.remove(evil_character)

                    generated_teams["minions"].clear()
                    generated_teams["demons"].clear()

                    if character not in modifier_characters:
                        modifier_characters.append(character)

                    # Atheista může chybějící místa zaplnit libovolnou kombinací
                    # Townsfolk a Outsiderů (mimo ty, kteří by přidali nějaké minion/demon).
                    available_good_characters = [
                        x
                        for x in script.townsfolk + script.outsiders
                        if generated_teams[x.team].count(x) < x.max_in_play
                        and x not in excluded_characters
                        and x.setup_modifier["add"].get("minions", 0) == 0
                        and x.setup_modifier["add"].get("demons", 0) == 0
                    ]

                    if evil_count > len(available_good_characters):
                        generation_failed = True
                        return GeneratedSetup(
                            generated_teams,
                            generation_failed,
                            [],
                            [],
                            []
                        )

                    new_good_characters = random.sample(
                        available_good_characters,
                        evil_count
                    )

                    for new_character in new_good_characters:
                        generated_teams[new_character.team].append(new_character)

                    characters_to_process.extend(new_good_characters)

                    if character.character_id == "atheist":
                        message.append("Ve hře nejsou žádné zlé postavy. Vypravěč může porušovat pravidla.")

                elif special["type"] == "x_outsiders":

                    if character not in modifier_characters:
                        modifier_characters.append(character)

                    # Xaan určuje výsledný počet Outsiderů bez ohledu
                    # na ostatní setup modifiery.
                    xaan_outsiders_count = random.randint(0, len(script.outsiders))

                    if xaan_outsiders_count == 0:
                        message.append("Xaan nikoho neotráví. X = 0")
                    else:
                        message.append(f"V {xaan_outsiders_count}. noci Xaan otráví všechny měšťany až do dalšího soumraku. X = {xaan_outsiders_count}")

            # Zapracujeme i nespeciální modifikátory:
            # ADD modifier
            for modifier_team, amount in modifier_add.items():

                if amount != 0 and character not in modifier_characters:
                    modifier_characters.append(character)

                # Přidávat lze pouze role, které ještě nedosáhly svého maximálního
                # povoleného počtu v setupu (defaultní hodnota max_in_play je 1).
                available_characters = [
                    x
                    for x in getattr(script, modifier_team)
                    if generated_teams[modifier_team].count(x) < x.max_in_play
                    and x not in excluded_characters
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

                # Již aktivované modifier role, či role chráněné
                # stále přítomným protectorem nesmějí být odstraněny.
                available_characters = [
                    x
                    for x in generated_teams[modifier_team]
                    if (
                        x not in modifier_characters
                        or (
                            x is character
                            # Hermit může odstranit sám sebe (kontrola se provádí pouze u special rolí).
                            and special
                            and special.get("self_removal_allowed", False)
                        )
                    )
                    and not any(
                        protector in team
                        for protector in protected_characters.get(x, [])
                        for team in generated_teams.values()
                    )
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

                # Role odebíráme jednotlivě, aby se u rolí povolených
                # vícekrát odstranil pouze vybraný počet jejich kopií.
                for character_to_remove in characters_to_remove:

                    generated_teams[modifier_team].remove(character_to_remove)

                    if character_to_remove in characters_to_process:
                        characters_to_process.remove(character_to_remove)

        # Počet outsiders nesedí, Xaan potřebuje korekci.
        if xaan_outsiders_count is not None:

            current_outsiders_count = len(generated_teams["outsiders"])

            if current_outsiders_count != xaan_outsiders_count:

                if current_outsiders_count > xaan_outsiders_count:
                    
                    available_outsiders = [
                        x
                        for x in generated_teams["outsiders"]
                        if x not in modifier_characters
                        and not any(
                            protector in team
                            for protector in protected_characters.get(x, [])
                            for team in generated_teams.values()
                        )
                    ]
                    available_townsfolk = [
                        x
                        for x in script.townsfolk
                        if generated_teams["townsfolk"].count(x) < x.max_in_play
                        and x not in excluded_characters
                    ]

                    if not available_outsiders or not available_townsfolk:
                        generation_failed = True
                        return GeneratedSetup(
                            generated_teams,
                            generation_failed,
                            [],
                            [],
                            []
                        )
                    
                    outsider_to_remove = random.choice(available_outsiders)
                    new_townsfolk = random.choice(available_townsfolk)

                    generated_teams["outsiders"].remove(outsider_to_remove)

                    if outsider_to_remove in characters_to_process:
                        characters_to_process.remove(outsider_to_remove)

                    generated_teams["townsfolk"].append(new_townsfolk)
                    characters_to_process.append(new_townsfolk)

                elif current_outsiders_count < xaan_outsiders_count:

                    available_outsiders = [
                        x
                        for x in script.outsiders
                        if generated_teams["outsiders"].count(x) < x.max_in_play
                        and x not in excluded_characters
                    ]
                    available_townsfolk = [                        
                        x
                        for x in generated_teams["townsfolk"]
                        if x not in modifier_characters
                        and not any(
                            protector in team
                            for protector in protected_characters.get(x, [])
                            for team in generated_teams.values()
                        )
                    ]

                    if not available_outsiders or not available_townsfolk:
                        generation_failed = True
                        return GeneratedSetup(
                            generated_teams,
                            generation_failed,
                            [],
                            [],
                            []
                        )
                    
                    townsfolk_to_remove = random.choice(available_townsfolk)
                    new_outsider = random.choice(available_outsiders)

                    generated_teams["townsfolk"].remove(townsfolk_to_remove)

                    if townsfolk_to_remove in characters_to_process:
                        characters_to_process.remove(townsfolk_to_remove)

                    generated_teams["outsiders"].append(new_outsider)
                    characters_to_process.append(new_outsider)
            
                # Xaan se pokouší o platný setup maximálně 20x
                xaan_correction_count += 1

                if xaan_correction_count >= 20:
                    generation_failed = True
                    return GeneratedSetup(
                        generated_teams,
                        generation_failed,
                        [],
                        [],
                        []
                    )

                continue

        # Fronta je prázdná. Xaan není ve hře, nebo už jeho počet Outsiderů sedí. Opuštíme while.
        break

    # Setup s Atheistou nesmí po zpracování žádného dalšího
    # modifieru obsahovat Miniony ani Démony.
    if no_evil and (generated_teams["minions"] or generated_teams["demons"]):
        generation_failed = True
        return GeneratedSetup(
            generated_teams,
            generation_failed,
            [],
            [],
            []
        )
    
    # ----- Bluffy -----

    # Vytvoříme seznam všech rolí (pro kontrolu bluffů a generování zpráv).
    generated_characters = [
        character
        for team in generated_teams.values()
        for character in team
    ]

    if not no_bluffs:
        
        # Bluffy mohou být pouze dobré role ze scriptu.
        good_characters = script.townsfolk + script.outsiders

        # Demon musí mít vždy tři platné bluffy.
        # Bluff nesmí být role ve hře a Opilec či Blázen nemohou být bluff nikdy.
        available_bluffs = [
            character
            for character in good_characters
            if character not in generated_characters
            and character.character_id not in ("drunk", "lunatic")
        ]

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

    else:
        bluffs = []

    # ----- Messages -----

    # Pokud je ve hře více než jeden Vesnický idiot, jeden z nich je opilý.
    village_idiot_count = sum(
        1
        for character in generated_characters
        if character.character_id == "villageidiot"
    )

    if village_idiot_count > 1:
        message.append("Jeden Vesnický idiot je opilý.")

    # Pokud je ve hře Blázen, hráč s žetonem Démona je
    # ve skutečnosti Blázen a pravý Démon je určen žetonem Blázna.
    lunatic = next(
        (
            character
            for character in generated_characters
            if character.character_id == "lunatic"
        ),
        None
    )

    if lunatic:
        message.append("Démon je ve skutečnosti Blázen.")
        message.append("Pravý démon je určen žetonem Blázna.")

    # Vědma má svou návnadu (Red Herring).
    fortune_teller = next(
        (
            character
            for character in generated_characters
            if character.character_id == "fortuneteller"
        ),
        None
    )

    if fortune_teller:
        message.append("Vědmě se jeden dobrý hráč jeví jako démon (Red Herring).")

    # Bounty Hunter způsobí, že jeden Townsfolk začne hru jako zlý.
    bounty_hunter = next(
        (
            character
            for character in generated_characters
            if character.character_id == "bountyhunter"
        ),
        None
    )

    if bounty_hunter:
        message.append("Jeden měšťan začne hru jako zlý.")

    # Snitch dává každému Minionovi tři bezpečné bluffy.
    # Jejich konkrétní výběr ponecháváme na Storytellerovi.
    snitch = next(
        (
            character
            for character in generated_characters
            if character.character_id == "snitch"
        ),
        None
    )

    if snitch:
        message.append("Každý přisluhovač dostane 3 bluffy z postav, které nejsou ve hře.")

    # ----- Úspěšný setup -----

    return GeneratedSetup(
        generated_teams,
        generation_failed,
        bluffs,
        message,
        generated_characters
    )