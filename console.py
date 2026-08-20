import sys

from script_loader import pre_loader
from menu import select_script, get_number_of_players, display_generated_setup
from application import application


def run_console():
    script_path = select_script(pre_loader())
    number_of_players = get_number_of_players()

    generated_setup, error = application(
        script_path,
        number_of_players
    )

    if error:
        print(error)
        sys.exit()

    display_generated_setup(generated_setup)


if __name__ == "__main__":
    run_console()