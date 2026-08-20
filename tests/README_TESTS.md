# Pytesty pro BotC Setup Generator

Balík testuje přímo generátor a loader, nikoliv GUI.

## Instalace

```bash
pip install pytest
```

## Umístění

Zkopíruj složku `tests/` a `pytest.ini` do kořene projektu, tedy vedle:

- `characters.json`
- `character.py`
- `script.py`
- `script_loader.py`
- souboru, který obsahuje `generate_setup()`

`conftest.py` se pokusí modul s `generate_setup()` najít automaticky.

## Spuštění

```bash
pytest
```

Podrobněji:

```bash
pytest -v
```

Jen loader:

```bash
pytest tests/test_script_loader.py -v
```

Jen setup modifiery:

```bash
pytest tests/test_generator_modifiers.py -v
```

## Co balík pokrývá

- základní počet hráčů
- platnost bluffů
- nedostatečně velký script
- Baron
- Drunk / remove_self
- Fang Gu
- Vigormortis
- Village Idiot / max_in_play
- Huntsman + Damsel
- Summoner / no_demon
- Atheist / no_evil
- Kazali / Lord of Typhon
- Legion
- Xaan
- Boffin
- loader s `_meta` i bez `_meta`
- travellers / fabled / loric
- abecední řazení pre_loaderu
- základní validaci `characters.json`
- regresní testy dříve nalezených chyb

## Poznámka k náhodnosti

Generátor smí některý náhodný pokus legitimně zahodit.
Helper `generate_success()` proto zkouší deterministické seedy 0–99
a vrátí první platný setup. Testy jsou díky tomu opakovatelné.

Pokud některý test selže, nejdřív spusť:

```bash
pytest -v -x
```

Tím se běh zastaví na první chybě a dostaneš nejčitelnější traceback.
