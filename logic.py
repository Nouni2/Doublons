import os
from PIL import Image
import shutil
from tqdm import tqdm
import time

def compare_images(img1, img2):
    try:
        image1 = Image.open(img1)
        image2 = Image.open(img2)
    except FileNotFoundError:
        return False  # Ignorer le fichier s'il n'existe pas

    return image1.tobytes() == image2.tobytes()

def identify_duplicates(folder_path):
    # Utiliser directement le dossier spécifié depuis l'interface
    photos_folder = folder_path
    files = [f for f in os.listdir(photos_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    duplicates_dict = {}
    marked_as_duplicates = set()

    for i, file1 in enumerate(tqdm(files, desc="Identification des doublons")):
        if file1 in marked_as_duplicates:
            continue

        file1_path = os.path.join(photos_folder, file1)
        base_name = os.path.splitext(file1)[0]

        # Initialiser la liste des doublons pour le fichier actuel
        duplicates = []

        for j, file2 in enumerate(files[i + 1:]):
            file2_path = os.path.join(photos_folder, file2)

            # Compare la taille
            try:
                size1 = os.path.getsize(file1_path)
            except FileNotFoundError:
                continue

            try:
                size2 = os.path.getsize(file2_path)
            except FileNotFoundError:
                continue

            # Compare la taille
            if size1 == size2:
                # Compare le contenu pixel par pixel
                if compare_images(file1_path, file2_path):
                    # Ajoute le fichier doublon à la liste
                    duplicates.append(file2)

                    # Marque le fichier comme ayant des doublons
                    marked_as_duplicates.add(file1)

        # Si des doublons ont été trouvés, ajoute le fichier et ses doublons au dictionnaire
        if duplicates:
            duplicates_dict[file1] = duplicates

    return duplicates_dict, marked_as_duplicates

def move_duplicates(duplicates_dict, marked_as_duplicates, folder_path):
    photos_folder = folder_path  # Utiliser directement le dossier spécifié
    output_folder = os.path.join(folder_path, "Doublons")
    temp_folder = os.path.join(folder_path, "Temp")

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    if not os.path.exists(temp_folder):
        os.makedirs(temp_folder)

    # Dictionnaire pour stocker les fichiers qui ont déjà été déplacés
    moved_files = {}

    # Dictionnaire pour stocker les fichiers qui ont des doublons mais ne doivent pas être déplacés
    marked_files = {}

    # Déplacement des fichiers du dossier temporaire vers le dossier de sortie
    for file, duplicates in tqdm(duplicates_dict.items(), desc="Déplacement des doublons"):
        # Vérifie si le fichier a déjà été déplacé
        if file not in moved_files and file not in marked_as_duplicates:
            # Copie le fichier d'origine dans le dossier temporaire
            shutil.copy2(os.path.join(photos_folder, file), os.path.join(temp_folder, file))
            moved_files[file] = True  # Marque le fichier comme déplacé

        # Copie les fichiers doublons dans le dossier temporaire
        for duplicate in duplicates:
            # Vérifie si le fichier doublon a déjà été déplacé
            if duplicate not in moved_files:
                shutil.copy2(os.path.join(photos_folder, duplicate), os.path.join(temp_folder, duplicate))
                moved_files[duplicate] = True  # Marque le fichier doublon comme déplacé

    # Suppression des fichiers d'origine
    for file in moved_files.keys():
        file_path = os.path.join(photos_folder, file)
        if os.path.exists(file_path):
            os.remove(file_path)

    # Déplacement des fichiers du dossier temporaire vers le dossier de sortie
    for temp_file in os.listdir(temp_folder):
        shutil.move(os.path.join(temp_folder, temp_file), os.path.join(output_folder, temp_file))

    # Suppression du dossier temporaire
    shutil.rmtree(temp_folder)

    # Génération des statistiques et des logs
    generate_stats_logs(folder_path, duplicates_dict, marked_files)




def generate_stats_logs(folder_path, duplicates_dict, marked_files):
    total_photos_folder = folder_path
    total_photos = len(os.listdir(total_photos_folder))

    total_duplicates_folder = os.path.join(folder_path, "Doublons")
    total_duplicates = len(os.listdir(total_duplicates_folder))

    total_files = total_photos + total_duplicates
    percentage_duplicates = (total_duplicates / total_files) * 100 if total_files > 0 else 0
    average_duplicates_per_file = total_duplicates / total_files if total_files > 0 else 0

    stats_file = os.path.join(folder_path, "stats.txt")
    stats_content = f"Nombre total de fichiers : {total_files}\n"
    stats_content += f"Nombre total de doublons : {total_duplicates}\n"
    stats_content += f"Pourcentage de doublons : {percentage_duplicates:.2f}%\n"
    stats_content += f"Nombre moyen de doublons par fichier : {average_duplicates_per_file:.2f}\n"

    # Ajout des statistiques supplémentaires
    stats_content += f"Temps d'exécution : {time.process_time()} secondes\n"

    with open(stats_file, "w", encoding="utf-8") as stats_file:
        stats_file.write(stats_content)

    logs_file = os.path.join(folder_path, "logs.txt")
    logs_content = ""
    for file, duplicates in duplicates_dict.items():
        if file not in marked_files:
            logs_content += f"Identifié les doublons pour {file}: {duplicates}\n"

    with open(logs_file, "w", encoding="utf-8") as logs_file:
        logs_file.write(logs_content)
