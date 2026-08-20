import tkinter as tk
from tkinter import ttk, filedialog
import tkinter.font as tkfont
from script_loader import pre_loader, import_script
from application import application
from character_loader import character_loader

def run_gui():
    pre_loaded_scripts = pre_loader()
    loaded_characters = character_loader()

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

    input_frame.columnconfigure(0, weight=4, uniform="input")
    input_frame.columnconfigure(1, weight=6, uniform="input")

    output_frame.columnconfigure(0, weight=4, uniform="output")
    output_frame.columnconfigure(1, weight=5, uniform="output")

    script_frame = tk.Frame(input_frame)

    # -------------------------
    # Fonts
    # -------------------------

    default_font = tkfont.nametofont("TkDefaultFont")

    title_font=default_font.copy()
    title_font.configure(
        size=18,
        weight="bold"
    )

    heading_font=default_font.copy()
    heading_font.configure(
        size=14,
        weight="bold"
    )

    text_font=default_font.copy()
    text_font.configure(
        size=14,
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

    script_frame.grid(
        row=1,
        column=1,
        sticky="we"
    )

    script_combobox = ttk.Combobox(
        script_frame,
        values=script_names,
        state="readonly",
    )
    script_combobox.grid(
        row=0,
        column=0,
        padx=10,
        pady=10,
        sticky="w",
    )
    script_combobox.current(0)


    def import_button_clicked():

        selected_file = filedialog.askopenfilename(
            title="Vyber script",
            filetypes=[("JSON soubory", "*.json")]
        )

        if not selected_file:
            return

        imported_path, error = import_script(
            selected_file,
            loaded_characters
        )

        if error:
            error_label.config(text=error)
            error_label.grid()
            return

        error_label.grid_remove()

        # Po importu znovu načteme dostupné scripty.
        updated_scripts = pre_loader()

        updated_script_names = [
            script["script_name"]
            for script in updated_scripts
        ]

        script_combobox.config(
            values=updated_script_names
        )

        # Vybereme právě importovaný script.
        for index, script in enumerate(updated_scripts):
            if script["script_path"].name == imported_path.name:
                script_combobox.current(index)
                break

        # Aktualizujeme seznam, který používá callback Generovat.
        pre_loaded_scripts.clear()
        pre_loaded_scripts.extend(updated_scripts)


    import_button = ttk.Button(
        script_frame,
        text="Importovat script",
        command=import_button_clicked,
    )

    import_button.grid(
        row=0,
        column=1,
        padx=(40, 0),
        pady=10,
    )


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


    error_label = tk.Label(
        output_frame,
        text="",
        font=text_font,
        fg="red",
        justify="center"
    )
    error_label.grid(
        row=6,
        column=0,
        columnspan=2,
        sticky="we",
        pady=10,
        padx=10,
    )
    error_label.grid_remove()

    # -------------------------
    # Generate button callback
    # -------------------------

    def hide_generated_setup():
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
        generated_message_label.grid_remove()

    def generate_button_clicked():
        selected_script_name = script_combobox.get()
        try:
            number_of_players = int(players_spinbox.get())
            if not 5 <= number_of_players <= 15:
                error_label.config(text="Zadejte celé číslo v rozsahu 5 - 15.")
                error_label.grid()
                hide_generated_setup()
                return
        except ValueError:
            error_label.config(text="Zadejte celé číslo v rozsahu 5 - 15.")
            error_label.grid()
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
            error_label.config(text=error)
            error_label.grid()
            hide_generated_setup()
            return
        
        error_label.grid_remove()


        townsfolk_text = "\n".join(
            character.name_cs
            for character in generated_setup.teams["townsfolk"]
        )
        if townsfolk_text:
            townsfolk_label.grid()
            generated_townsfolk_label.grid()
        else:
            townsfolk_label.grid_remove()
            generated_townsfolk_label.grid_remove()
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
        if minions_text:
            minions_label.grid()
            generated_minions_label.grid()
        else:
            minions_label.grid_remove()
            generated_minions_label.grid_remove()
        generated_minions_label.config(text=minions_text)


        demons_text = "\n".join(
            character.name_cs
            for character in generated_setup.teams["demons"]
        )
        if demons_text:
            demons_label.grid()
            generated_demons_label.grid()
        else:
            demons_label.grid_remove()
            generated_demons_label.grid_remove()
        generated_demons_label.config(text=demons_text)

        bluffs_text = ", ".join(
            character.name_cs
            for character in generated_setup.bluffs
        )
        if bluffs_text:
            bluffs_label.grid()
            generated_bluffs_label.grid()
        else:
            bluffs_label.grid_remove()
            generated_bluffs_label.grid_remove()
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