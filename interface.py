# interface.py

import os
import subprocess
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import sys


class InterfaceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Interface pour votre Script")
        self.folder_path = tk.StringVar()

        self.create_widgets()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def create_widgets(self):
        label = ttk.Label(self.root, text="Sélectionnez le dossier de travail :")
        label.grid(column=0, row=0, pady=10, padx=10)

        entry = ttk.Entry(self.root, textvariable=self.folder_path, width=40)
        entry.grid(column=1, row=0, pady=10)

        browse_button = ttk.Button(self.root, text="Parcourir", command=self.browse_folder)
        browse_button.grid(column=2, row=0, pady=10, padx=10)

        run_button = ttk.Button(self.root, text="Exécuter", command=self.run_script)
        run_button.grid(column=0, row=1, columnspan=3, pady=10)

        # Barre de progression
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.root, length=200, mode="determinate", variable=self.progress_var)
        self.progress_bar.grid(column=0, row=2, columnspan=3, pady=10)

    def browse_folder(self):
        folder_selected = filedialog.askdirectory()
        self.folder_path.set(folder_selected)

    def update_progress(self, value):
        self.progress_var.set(value)

    def check_process(self, script_thread):
        if script_thread.poll() is None:
            # Si le processus n'est pas terminé, continue à vérifier
            self.root.after(100, lambda: self.check_process(script_thread))
        else:
            # Le processus est terminé, exécutez la fonction de fin
            self.process_finished(script_thread)

    def process_finished(self, script_thread):
        # Lire la sortie finale après la fin de l'exécution du script
        final_output = script_thread.stdout.read().decode("utf-8")
        print(final_output)

    def run_script(self):
        folder_path_str = self.folder_path.get()
        logic_path = os.path.join(os.path.dirname(__file__), "main.py")

        if not os.path.exists(logic_path):
            print("Erreur: Le script principal (main.py) n'a pas été trouvé dans le même répertoire.")
            return

        # Lancer le script principal avec le dossier spécifié
        command = f"python {logic_path} {folder_path_str}"
        subprocess.Popen(command, shell=True)

    def on_close(self):
        # Fermer l'interface et quitter le programme
        self.root.destroy()
        sys.exit()

if __name__ == "__main__":
    root = tk.Tk()
    app_interface = InterfaceApp(root)
    root.mainloop()
