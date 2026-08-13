import tkinter as tk
from tkinter import ttk
import tkinter.font as tkfont
from script_loader import pre_loader
from application import application


def run_gui():
    pre_loaded_scripts = pre_loader()

    script_names = [
        pre_loaded_script["script_name"]
        for pre_loaded_script in pre_loaded_scripts
    ]

    root = tk.Tk()

    root.title("BotC Setup Generator")
    root.geometry("800x850+400+20")
    root.minsize(400, 400)

    root.columnconfigure(0, weight=1)

    input_frame = tk.Frame(root)
    input_frame.grid(
        row=0,
        column=0,
        sticky="ew"
    )

    output_frame = tk.Frame(root)
    output_frame.grid(
        row=1,
        column=0,
        sticky="ew"
    )

    input_frame.columnconfigure(0, weight=1, uniform="input")
    input_frame.columnconfigure(1, weight=1, uniform="input")

    output_frame.columnconfigure(0, weight=1, uniform="output")
    output_frame.columnconfigure(1, weight=1, uniform="output")

    # -------------------------
    # Fonts
    # -------------------------

    default_font = tkfont.nametofont("TkDefaultFont")

    title_font=default_font.copy()
    title_font.configure(
        size=20,
        weight="bold"
    )

    heading_font=default_font.copy()
    heading_font.configure(
        size=15,
        weight="bold"
    )

    text_font=default_font.copy()
    text_font.configure(
        size=15,
    )


    # -------------------------
    # Input section
    # -------------------------


    title_label = tk.Label(
        input_frame,
        text="BotC Setup Generator",
        font=title_font,
    )
    title_label.grid(
        row=0,
        column=0,
        columnspan=2,
        sticky="we",
        pady=20,
    )

    script_label = tk.Label(
        input_frame,
        text="Zvolte script:",
    )
    script_label.grid(
        row=1,
        column=0,
        sticky="e",
    )

    script_combobox = ttk.Combobox(
        input_frame,
        values=script_names,
        state="readonly",
    )
    script_combobox.grid(
        row=1,
        column=1,
        padx=10,
        pady=10,
        sticky="w",
    )
    script_combobox.current(0)


    players_label = tk.Label(
        input_frame,
        text="Zvolte počet hráčů:",
    )
    players_label.grid(
        row=2,
        column=0,
        sticky="e",
    )

    players_spinbox = ttk.Spinbox(
        input_frame,
        from_=5,
        to=15,
    )
    players_spinbox.grid(
        row=2,
        column=1,
        padx=10,
        pady=10,
        sticky="w",
    )
    players_spinbox.set(8)

    # -------------------------
    # Output section
    # -------------------------

    townsfolk_label = tk.Label(
        output_frame,
        text="Měšťané:",
        font=heading_font,
        fg="blue",
    )
    townsfolk_label.grid(
        row=0,
        column=0,
        sticky="ne",
        pady=5,
        padx=10,
    )
    townsfolk_label.grid_remove()

    generated_townsfolk_label = tk.Label(
        output_frame,
        text="",
        font=text_font,
        fg="blue",
        justify="left"
    )
    generated_townsfolk_label.grid(
        row=0,
        column=1,
        sticky="w",
        pady=5,
        padx=10,
    )
    generated_townsfolk_label.grid_remove()


    outsiders_label = tk.Label(
        output_frame,
        text="Podivíni:",
        font=heading_font,
        fg="blue",
    )
    outsiders_label.grid(
        row=1,
        column=0,
        sticky="ne",
        pady=5,
        padx=10,
    )
    outsiders_label.grid_remove()


    generated_outsiders_label = tk.Label(
        output_frame,
        text="",
        font=text_font,
        fg="blue",
        justify="left"
    )
    generated_outsiders_label.grid(
        row=1,
        column=1,
        sticky="w",
        pady=5,
        padx=10,
    )
    generated_outsiders_label.grid_remove()


    minions_label = tk.Label(
        output_frame,
        text="Přisluhovači:",
        font=heading_font,
        fg="red",
    )
    minions_label.grid(
        row=2,
        column=0,
        sticky="ne",
        pady=5,
        padx=10,
    )
    minions_label.grid_remove()

    generated_minions_label = tk.Label(
        output_frame,
        text="",
        font=text_font,
        fg="red",
        justify="left"
    )
    generated_minions_label.grid(
        row=2,
        column=1,
        sticky="w",
        pady=5,
        padx=10,
    )
    generated_minions_label.grid_remove()


    demons_label = tk.Label(
        output_frame,
        text="Démon:",
        font=heading_font,
        fg="red",
    )
    demons_label.grid(
        row=3,
        column=0,
        sticky="ne",
        pady=5,
        padx=10,
    )
    demons_label.grid_remove()

    generated_demons_label = tk.Label(
        output_frame,
        text="",
        font=text_font,
        fg="red",
        justify="left"
    )
    generated_demons_label.grid(
        row=3,
        column=1,
        sticky="w",
        pady=5,
        padx=10,
    )
    generated_demons_label.grid_remove()


    bluffs_label = tk.Label(
        output_frame,
        text="Bluffy pro démona:",
        font=text_font,
        fg="red",
    )
    bluffs_label.grid(
        row=4,
        column=0,
        sticky="ne",
        pady=10,
        padx=10,
    )
    bluffs_label.grid_remove()

    generated_bluffs_label = tk.Label(
        output_frame,
        text="",
        font=text_font,
        fg="blue",
        justify="left"
    )
    generated_bluffs_label.grid(
        row=4,
        column=1,
        sticky="w",
        pady=10,
        padx=10,
    )
    generated_bluffs_label.grid_remove()


    generated_message_label = tk.Label(
        output_frame,
        text="",
        font=heading_font,
        justify="center"
    )
    generated_message_label.grid(
        row=5,
        column=0,
        columnspan=2,
        sticky="we",
        pady=10,
        padx=10,
    )
    generated_message_label.grid_remove()




    # -------------------------
    # Generate button callback
    # -------------------------

    def hide_generated_setup():
        generated_message_label.grid()
        townsfolk_label.grid_remove()
        generated_townsfolk_label.grid_remove()
        outsiders_label.grid_remove()
        generated_outsiders_label.grid_remove()
        minions_label.grid_remove()
        generated_minions_label.grid_remove()
        demons_label.grid_remove()
        generated_demons_label.grid_remove()
        bluffs_label.grid_remove()
        generated_bluffs_label.grid_remove()

    def generate_button_clicked():
        selected_script_name = script_combobox.get()
        try:
            number_of_players = int(players_spinbox.get())
            if not 5 <= number_of_players <= 15:
                generated_message_label.config(text="Zadejte celé číslo v rozsahu 5 - 15.")
                hide_generated_setup()
                return
        except ValueError:
            generated_message_label.config(text="Zadejte celé číslo v rozsahu 5 - 15.")
            hide_generated_setup()
            return

        for pre_loaded_script in pre_loaded_scripts:
            if pre_loaded_script["script_name"] == selected_script_name:
                selected_script_path = pre_loaded_script["script_path"]
                break
        
        generated_setup, error = application(
            selected_script_path,
            number_of_players
        )

        if error:
            generated_message_label.config(text=error)
            hide_generated_setup()
            return


        townsfolk_text = "\n".join(
            character.name_cs
            for character in generated_setup.teams["townsfolk"]
        )
        townsfolk_label.grid()
        generated_townsfolk_label.grid()
        generated_townsfolk_label.config(text=townsfolk_text)


        outsiders_text = "\n".join(
            character.name_cs
            for character in generated_setup.teams["outsiders"]
        )
        if outsiders_text:
            outsiders_label.grid()
            generated_outsiders_label.grid()
        else:
            outsiders_label.grid_remove()        
            generated_outsiders_label.grid_remove()
        generated_outsiders_label.config(text=outsiders_text)


        minions_text = "\n".join(
            character.name_cs
            for character in generated_setup.teams["minions"]
        )
        minions_label.grid()
        generated_minions_label.grid()
        generated_minions_label.config(text=minions_text)


        demons_text = "\n".join(
            character.name_cs
            for character in generated_setup.teams["demons"]
        )
        demons_label.grid()
        generated_demons_label.grid()
        generated_demons_label.config(text=demons_text)

        bluffs_text = ", ".join(
            character.name_cs
            for character in generated_setup.bluffs
        )
        bluffs_label.grid()
        generated_bluffs_label.grid()
        generated_bluffs_label.config(text=bluffs_text)

        message_text = "\n".join(
            message
            for message in generated_setup.message
        )
        if message_text:
            generated_message_label.grid()
        else:
            generated_message_label.grid_remove()
        generated_message_label.config(text=message_text)



    generate_button = ttk.Button(
        input_frame,
        text="Generovat",
        command=generate_button_clicked,
    )
    generate_button.grid(
        row=3,
        column=0,
        columnspan=2,
        pady=10,
    )


    root.mainloop()