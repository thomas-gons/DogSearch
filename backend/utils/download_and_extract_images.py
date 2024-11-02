import os
import tarfile
import yaml
import requests
from pathlib import Path
from tqdm import tqdm

# Chemin vers le fichier de configuration
CONFIG_FILE = Path("config.yaml")
# Dossier de destination pour les images
DESTINATION_FOLDER = Path("resources")

def load_config():
    """Charge le fichier de configuration YAML."""
    with open(CONFIG_FILE, "r") as f:
        config = yaml.safe_load(f)
    return config

def download_dataset(url, destination):
    """Télécharge le fichier .tar à partir de l'URL et le sauvegarde à l'emplacement spécifié."""
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        total_size = int(response.headers.get('content-length', 0))
        destination.parent.mkdir(parents=True, exist_ok=True)  # Crée les dossiers parents si nécessaire
        
        with open(destination, "wb") as f, tqdm(
            total=total_size, unit='B', unit_scale=True, desc=destination.name
        ) as pbar:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                pbar.update(len(chunk))

        print(f"Téléchargement terminé : {destination}")
    else:
        raise Exception(f"Échec du téléchargement. Statut HTTP : {response.status_code}")

def extract_tarfile(tar_path, extract_to):
    """Décompresse le fichier .tar dans le répertoire cible."""
    with tarfile.open(tar_path, "r") as tar:
        tar.extractall(path=extract_to)
    print(f"Extraction terminée dans : {extract_to}")

def download_and_prepare_images():
    """Télécharge et extrait les images si elles ne sont pas déjà présentes."""
    # Charger la configuration
    config = load_config()
    dataset_url = config.get("dataset_image_url")
    if not dataset_url:
        raise ValueError("URL du dataset non trouvée dans le fichier config.yaml")

    # Chemin pour sauvegarder l'archive téléchargée
    tar_path = DESTINATION_FOLDER / "images.tar"

    # Vérifier si les images sont déjà extraites
    if DESTINATION_FOLDER.exists() and any(DESTINATION_FOLDER.iterdir()):
        print(f"Images déjà extraites dans {DESTINATION_FOLDER}")
        return

    # Téléchargement du dataset
    print("Téléchargement du dataset...")
    download_dataset(dataset_url, tar_path)

    # Extraction de l'archive
    print("Extraction du fichier tar...")
    extract_tarfile(tar_path, DESTINATION_FOLDER)

    # Suppression de l'archive après extraction
    tar_path.unlink()  # Utiliser .unlink() pour supprimer un Path object
    print("Archive supprimée après extraction.")
