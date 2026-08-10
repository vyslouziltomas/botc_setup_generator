import sys

def select_script(pre_loaded_scripts):

    print("\nSeznam dostupných scriptů:\n")

    for i, pre_loaded_script in enumerate(pre_loaded_scripts, start = 1):
        print(f"{i} - {pre_loaded_script["script_name"]}")
    
    print("\n0 - Ukonči program")

    while True:

        try:
            selected_script = int(input("\nVyber script: "))

            if selected_script == 0:
                sys.exit()

            elif 1 <= selected_script <= len(pre_loaded_scripts):
                
                return pre_loaded_scripts[selected_script - 1]["script_path"]
            
            else:
                print("\nNeplatná volba")

        except ValueError:    
            print("\nNeplatná volba")

def get_number_of_players():

    while True:
        try:
            number_of_players = int(input("\nZadej počet hráčů: "))

            if 5 <= number_of_players <= 15:

                return number_of_players
            
            print("\nZadejte celé číslo v rozsahu 5 - 15.")

        except ValueError:    
            print("\nZadejte celé číslo v rozsahu 5 - 15.")


def display_generated_setup(generated_setup):

    bluffs = generated_setup.bluffs
    message = generated_setup.message

    print("\nMěšťané:\n")
    for character in generated_setup.teams["townsfolk"]:
        print(character.name_cs)

    print("\nPodivíni:\n")
    for character in generated_setup.teams["outsiders"]:
        print(character.name_cs)

    print("\nPřisluhovači:\n")
    for character in generated_setup.teams["minions"]:
        print(character.name_cs)

    print("\nDémon:\n")
    for character in generated_setup.teams["demons"]:
        print(character.name_cs)

    print("\nBluffy:\n")
    for bluff in bluffs:
        print(bluff.name_cs)

    print("")
    if message:
        for text in message:
            print(text)
        print("")