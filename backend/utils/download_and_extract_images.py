import tarfile
import requests
from tqdm import tqdm
from config import config

import os

class DatasetHandler():

    def __init__(self) -> None:
        self.dataset_path = os.Path(config['dataset_path'])
        self.dataset_archive_path = self.dataset_path + 'images.tar'
    
    
    def download_dataset(self, url):
        """Télécharge le fichier .tar à partir de l'URL et le sauvegarde à l'emplacement spécifié."""
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            total_size = int(response.headers.get('content-length', 0))
            self.dataset_path.parent.mkdir(parents=True, exist_ok=True)  # Crée les dossiers parents si nécessaire
            
            with open(self.dataset_path, "wb") as f, tqdm(
                total=total_size, unit='B', unit_scale=True, desc=self.dataset_path.name
            ) as pbar:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    pbar.update(len(chunk))

            print(f"Téléchargement terminé : {self.dataset_path}")
        else:
            raise Exception(f"Échec du téléchargement. Statut HTTP : {response.status_code}")


    def extract_tarfile(self):
        """Décompresse le fichier .tar dans le répertoire cible."""
        with tarfile.open(self.dataset_archive_path.data, "r") as tar:
            tar.extractall(path=self.dataset_path)
        print(f"Extraction terminée dans : {self.dataset_path}")


    def download_and_prepare_images():
        """Télécharge et extrait les images si elles ne sont pas déjà présentes."""
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
