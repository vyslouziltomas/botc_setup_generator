import pytest

from conftest import (
    GENERATOR_MODULE,
    flatten,
    ids,
    make_script,
    player_setup,
    result_failed,
    result_messages,
    result_teams,
)


def _first_sample(population, k):
    """
    Deterministická náhrada random.sample().

    Vrací první k položek beze změny pořadí. Používáme ji pouze
    v testech, kde potřebujeme přesně určit pořadí zpracování rolí.
    """
    return list(population)[:k]


def _choose_character(target):
    """
    Vrátí funkci vhodnou pro monkeypatch random.choice().

    Pokud je cílová postava mezi možnostmi, vybere ji.
    V ostatních případech vezme první dostupnou možnost.
    """
    def choose(options):
        if target in options:
            return target

        return options[0]

    return choose


def test_boffin_ability_is_not_in_play(monkeypatch, characters):
    """
    Boffin musí vybrat schopnost dobré role, která není ve hře.

    V základním setupu proto nevylosujeme žádného Townsfolka.
    Boffinovi deterministicky přidělíme schopnost Chefa a ověříme,
    že Chef zůstane mimo výsledný setup.
    """
    if "boffin" not in characters or "chef" not in characters:
        pytest.skip("characters.json neobsahuje Boffina nebo Chefa.")

    chef = characters["chef"]

    script = make_script(
        characters,
        townsfolk=("chef",),
        minions=("boffin",),
        extra_townsfolk=5,
        extra_demons=1,
    )

    setup = player_setup(
        townsfolk=0,
        outsiders=0,
        minions=1,
        demons=1,
    )

    # Boffin si vždy zvolí Chefa, pokud je mezi dostupnými abilities.
    monkeypatch.setattr(
        GENERATOR_MODULE.random,
        "choice",
        _choose_character(chef),
    )

    result = GENERATOR_MODULE.generate_setup(script, setup)

    assert result_failed(result) is False

    generated_ids = ids(flatten(result_teams(result)))

    # Boffin schopnost musí zůstat not-in-play.
    assert "chef" not in generated_ids

    # Samotný Boffin samozřejmě ve hře zůstává.
    assert "boffin" in generated_ids


def test_boffin_excluded_ability_is_not_added_by_xaan(
    monkeypatch,
    characters,
):
    """
    Role vybraná Boffinem se přidá do excluded_characters.

    Následná Xaanova korekce proto nesmí tuto roli použít jako
    nového Townsfolka, i když by jinak byla pro výběr dostupná.
    """
    required = {"boffin", "xaan", "chef"}

    if not required.issubset(characters):
        pytest.skip("characters.json neobsahuje Boffina, Xaana nebo Chefa.")

    chef = characters["chef"]

    script = make_script(
        characters,
        townsfolk=("chef",),
        minions=("boffin", "xaan"),
        extra_townsfolk=6,
        extra_outsiders=2,
        extra_demons=1,
    )

    setup = player_setup(
        townsfolk=0,
        outsiders=1,
        minions=2,
        demons=1,
    )

    # Zachováme pořadí minionů: Boffin se musí zpracovat před Xaanem.
    monkeypatch.setattr(
        GENERATOR_MODULE.random,
        "sample",
        _first_sample,
    )

    # Boffin vybere Chefa. Při ostatních choice() výběrech se použije
    # první dostupná možnost.
    monkeypatch.setattr(
        GENERATOR_MODULE.random,
        "choice",
        _choose_character(chef),
    )

    # X = 0 znamená, že musí odstranit jediného Outsidera
    # a nahradit ho Townsfolkem.
    monkeypatch.setattr(
        GENERATOR_MODULE.random,
        "randint",
        lambda _start, _end: 0,
    )

    result = GENERATOR_MODULE.generate_setup(script, setup)

    assert result_failed(result) is False

    teams = result_teams(result)
    generated_ids = ids(flatten(teams))

    # Xaan skutečně provedl korekci na 0 Outsiderů.
    assert len(teams["outsiders"]) == 0

    # Chef byl Boffinova ability, takže ho Xaan nesměl přidat.
    assert "chef" not in generated_ids

    assert "boffin" in generated_ids
    assert "xaan" in generated_ids


def test_boffin_village_idiot_does_not_activate_duplicate_self(
    monkeypatch,
    characters,
):
    """
    Village Idiot je speciální Boffin jinx.

    Pokud Boffin získá jeho schopnost, nesmí se spustit
    setup modifier duplicate_self. Village Idiot tedy není
    kvůli Boffinovi přidán do hry ani duplikován.
    """
    required = {"boffin", "villageidiot"}

    if not required.issubset(characters):
        pytest.skip("characters.json neobsahuje Boffina nebo Village Idiota.")

    village_idiot = characters["villageidiot"]

    script = make_script(
        characters,
        townsfolk=("villageidiot",),
        minions=("boffin",),
        extra_townsfolk=5,
        extra_demons=1,
    )

    setup = player_setup(
        townsfolk=0,
        outsiders=0,
        minions=1,
        demons=1,
    )

    monkeypatch.setattr(
        GENERATOR_MODULE.random,
        "choice",
        _choose_character(village_idiot),
    )

    result = GENERATOR_MODULE.generate_setup(script, setup)

    assert result_failed(result) is False

    generated_ids = ids(flatten(result_teams(result)))

    # VI je pouze schopnost Boffina, nikoliv role ve hře.
    assert "villageidiot" not in generated_ids

    # Tím zároveň ověřujeme, že se nespustil duplicate_self.
    assert generated_ids.count("villageidiot") == 0


def test_xaan_cannot_remove_character_protected_by_huntsman(
    monkeypatch,
    characters,
):
    """
    Huntsman přidá Damsel a chrání ji přes protected_characters.

    Pokud potom Xaan požaduje X = 0, potřeboval by jediného
    Outsidera odstranit. Damsel ale odstranit nesmí, takže je
    správným výsledkem neúspěšný pokus o generování.
    """
    required = {"huntsman", "damsel", "xaan"}

    if not required.issubset(characters):
        pytest.skip("characters.json neobsahuje Huntsmana, Damsel nebo Xaana.")

    script = make_script(
        characters,
        townsfolk=("huntsman",),
        outsiders=("damsel",),
        minions=("xaan",),
        extra_townsfolk=5,
        extra_outsiders=1,
        extra_demons=1,
    )

    setup = player_setup(
        townsfolk=2,
        outsiders=0,
        minions=1,
        demons=1,
    )

    # Deterministické základní losování: Huntsman bude určitě ve hře.
    monkeypatch.setattr(
        GENERATOR_MODULE.random,
        "sample",
        _first_sample,
    )

    # Xaan chce výsledný počet Outsiderů 0.
    monkeypatch.setattr(
        GENERATOR_MODULE.random,
        "randint",
        lambda _start, _end: 0,
    )

    result = GENERATOR_MODULE.generate_setup(script, setup)

    # Huntsman přidal Damsel, ale Xaan ji kvůli ochraně nesmí odstranit.
    # Proto není možné X = 0 splnit a tento generační pokus musí selhat.
    assert result_failed(result) is True


def test_kazali_preempts_baron_modifier(monkeypatch, characters):
    """
    Kazali kompletně přepisuje normální evil setup.

    I když je v původním losování Baron, Kazali se musí zpracovat
    jako první. Baron tedy nesmí aplikovat +2 Outsiders / -2 Townsfolk
    před Kazaliho regenerací.
    """
    required = {"kazali", "baron"}

    if not required.issubset(characters):
        pytest.skip("characters.json neobsahuje Kazaliho nebo Barona.")

    script = make_script(
        characters,
        minions=("baron",),
        demons=("kazali",),
        extra_townsfolk=12,
        extra_outsiders=6,
    )

    setup = player_setup(
        townsfolk=5,
        outsiders=0,
        minions=1,
        demons=1,
    )

    monkeypatch.setattr(
        GENERATOR_MODULE.random,
        "sample",
        _first_sample,
    )

    # U Kazaliho zvolíme 0 Outsiderů, pokud je tato možnost dostupná.
    monkeypatch.setattr(
        GENERATOR_MODULE.random,
        "choices",
        lambda population, weights=None, k=1: [
            0 if 0 in population else population[0]
        ],
    )

    result = GENERATOR_MODULE.generate_setup(script, setup)

    assert result_failed(result) is False

    teams = result_teams(result)

    # Kazali ruší běžné Miniony.
    assert teams["minions"] == []

    # Původních 5 Townsfolk + 1 Minion slot se změnilo na 6 good rolí.
    assert len(teams["townsfolk"]) + len(teams["outsiders"]) == 6

    # Baron se nesmí v setupu zachovat.
    assert "baron" not in ids(flatten(teams))

    # Kazali zůstává jediným Démonem.
    assert ids(teams["demons"]) == ["kazali"]


def test_legion_discards_previous_drunk_state(monkeypatch, characters):
    """
    Legie kompletně regenerují setup a zahazují předchozí pomocný stav.

    Do základního losování vložíme Drunka, ale Legii generátor
    přesune na začátek fronty. Drunk proto nesmí před resetem
    vytvořit svou message ani ovlivnit výsledné složení.
    """
    required = {"legion", "drunk"}

    if not required.issubset(characters):
        pytest.skip("characters.json neobsahuje Legii nebo Drunka.")

    script = make_script(
        characters,
        outsiders=("drunk",),
        demons=("legion",),
        extra_townsfolk=15,
        extra_outsiders=6,
        extra_minions=3,
    )

    setup = player_setup(
        townsfolk=7,
        outsiders=1,
        minions=1,
        demons=1,
    )

    monkeypatch.setattr(
        GENERATOR_MODULE.random,
        "sample",
        _first_sample,
    )

    # Legion setup preferujeme bez Outsiderů, aby se Drunk
    # nemohl znovu objevit až při regeneraci good rolí.
    monkeypatch.setattr(
        GENERATOR_MODULE.random,
        "choices",
        lambda population, weights=None, k=1: [
            0 if 0 in population else population[0]
        ],
    )

    result = GENERATOR_MODULE.generate_setup(script, setup)

    assert result_failed(result) is False

    teams = result_teams(result)
    messages = result_messages(result)

    # Drunk z původního losování se nesmí přenést přes Legion reset.
    assert "drunk" not in ids(flatten(teams))
    assert "Jeden měšťan je ve skutečnosti Opilec." not in messages

    # Celkový počet hráčů musí zůstat zachovaný.
    assert len(flatten(teams)) == 10

    # Legion setup musí skutečně obsahovat více Legií.
    assert ids(teams["demons"]).count("legion") > 1