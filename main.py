# main.py

import logic
import sys
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("folder_path", help="Chemin du dossier de travail")
    parser.add_argument("--progress_file", help="Fichier temporaire pour stocker la progression")
    args = parser.parse_args()

    folder_path = args.folder_path

    # Étape 1 : Identification des doublons
    duplicates_dict, marked_as_duplicates = logic.identify_duplicates(folder_path)

    # Étape 2 : Déplacement des doublons
    logic.move_duplicates(duplicates_dict, marked_as_duplicates, folder_path)

if __name__ == "__main__":
    main()
