# interface.py

import os
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import threading
import sys
import logic

class InterfaceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Doublons Finder")
        self.folder_path = tk.StringVar()
        self.output_text = tk.StringVar()

        self.create_widgets()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.progress_messages = ""

    def create_widgets(self):
        label = ttk.Label(self.root, text="Sélectionnez le dossier de travail :")
        label.grid(column=0, row=0, pady=10, padx=10)

        entry = ttk.Entry(self.root, textvariable=self.folder_path, width=40)
        entry.grid(column=1, row=0, pady=10)

        browse_button = ttk.Button(self.root, text="Parcourir", command=self.browse_folder)
        browse_button.grid(column=2, row=0, pady=10, padx=10)

        run_button = ttk.Button(self.root, text="Exécuter", command=self.run_script)
        run_button.grid(column=0, row=1, columnspan=3, pady=10)

        # Étiquettes pour les barres de progression
        ttk.Label(self.root, text=" Identification des doublons :").grid(column=0, row=2, pady=5, sticky=tk.W)
        ttk.Label(self.root, text=" Déplacement des doublons :").grid(column=0, row=3, pady=5, sticky=tk.W)

        # Barre de progression pour l'identification des doublons
        self.progress_var_identification = tk.DoubleVar()
        self.progress_bar_identification = ttk.Progressbar(self.root, length=200, mode="determinate",
                                                           variable=self.progress_var_identification)
        self.progress_bar_identification.grid(column=1, row=2, columnspan=2, pady=5, sticky=tk.W)

        # Barre de progression pour le déplacement des doublons
        self.progress_var_deplacement = tk.DoubleVar()
        self.progress_bar_deplacement = ttk.Progressbar(self.root, length=200, mode="determinate",
                                                       variable=self.progress_var_deplacement)
        self.progress_bar_deplacement.grid(column=1, row=3, columnspan=2, pady=5, sticky=tk.W)

        # Widget de texte pour afficher la progression dans la console et l'interface
        output_text_widget = ttk.Label(self.root, textvariable=self.output_text)
        output_text_widget.grid(column=0, row=4, columnspan=3, pady=10, padx=10)

    def browse_folder(self):
        folder_selected = filedialog.askdirectory()
        self.folder_path.set(folder_selected)

    def update_identification_progress(self):
        if logic.total_files_identification == 0:
            return
        percentage = (logic.processed_files_identification / logic.total_files_identification) * 100
        self.update_progress_identification(percentage)

    def update_deplacement_progress(self):
        if logic.total_files_deplacement == 0:
            return
        percentage = (logic.processed_files_deplacement / logic.total_files_deplacement) * 100
        self.update_progress_deplacement(percentage)

    def update_progress_identification(self, value):
        self.progress_var_identification.set(value)
        message = f"Identification des doublons : {round(value)}%"
        self.progress_messages = message
        self.output_text.set(self.progress_messages)

    def update_progress_deplacement(self, value):
        self.progress_var_deplacement.set(value)
        message = f"Déplacement des doublons : {round(value)}%"
        self.progress_messages = message
        self.output_text.set(self.progress_messages)

    def process_finished(self, script_thread):
        # Lire la sortie finale après la fin de l'exécution du script
        final_output = script_thread.stdout.read()
        print(final_output)
        self.progress_messages = "Processus terminé avec succès."
        self.output_text.set(self.progress_messages)

    def check_process(self, script_thread):
        if script_thread.poll() is None:
            # Si le processus n'est pas terminé, continue à vérifier
            self.root.after(100, lambda: self.check_process(script_thread))
        else:
            # Le processus est terminé, exécutez la fonction de fin
            self.process_finished(script_thread)


    def run_script(self):
        folder_path_str = self.folder_path.get()
        logic_path = os.path.join(os.path.dirname(__file__), "main.py")

        if not os.path.exists(logic_path):
            print("Erreur: Le script principal (main.py) n'a pas été trouvé dans le même répertoire.")
            return

        # Lancer le script principal avec le dossier spécifié dans un thread séparé
        script_thread = threading.Thread(target=self.run_script_thread, args=(logic_path, folder_path_str))
        script_thread.start()

    def run_script_thread(self, logic_path, folder_path_str):
        # Exécuter le script principal dans un thread séparé
        global total_files_identification
        global total_files_deplacement

        duplicates_dict, marked_as_duplicates = logic.identify_duplicates(folder_path_str,
                                                                          self.update_progress_identification)
        self.duplicates_dict = duplicates_dict
        self.marked_as_duplicates = marked_as_duplicates
        total_files_identification = len(duplicates_dict)
        total_files_deplacement = len(duplicates_dict)

        logic.move_duplicates(duplicates_dict, marked_as_duplicates, folder_path_str, self.update_progress_deplacement)

    def on_close(self):
        # Fermer l'interface et quitter le programme
        self.root.destroy()
        sys.exit()

    def check_for_updates(self):
        self.update_identification_progress()
        self.update_deplacement_progress()
        self.root.after(100, self.check_for_updates)

if __name__ == "__main__":
    root = tk.Tk()
    app_interface = InterfaceApp(root)
    root.after(100, app_interface.check_for_updates)  # Lancer la vérification des mises à jour
    root.mainloop()
