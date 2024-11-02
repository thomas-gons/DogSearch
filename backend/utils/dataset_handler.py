import base64
import tarfile
import requests
from tqdm import tqdm
from pathlib import Path
from .config import config
from orm import orm


class DatasetHandler:
    def __init__(self) -> None:
        self.dataset_path = Path(config['dataset_path'])
        self.dataset_archive_path = self.dataset_path / 'images.tar'
        self.image_paths_file = Path(config['image_paths'])

    def __download_dataset(self, url: str):
        """Download the .tar file from the URL and save it to the specified location."""
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            total_size = int(response.headers.get('content-length', 0))
            self.dataset_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.dataset_path, "wb") as f, tqdm(
                total=total_size, unit='B', unit_scale=True, desc=self.dataset_path.name
            ) as pbar:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    pbar.update(len(chunk))

            print(f"Download completed: {self.dataset_path}")
        else:
            raise Exception(f"Download failed. HTTP Status: {response.status_code}")

    def __extract_tarfile(self):
        """Extract the .tar file into the target directory."""
        with tarfile.open(self.dataset_archive_path.data, "r") as tar:
            tar.extractall(path=self.dataset_path)
        print(f"Extraction completed at: {self.dataset_path}")

    def __save_to_db(self):
        """Save the previously extracted images to the database."""
        with open(self.image_paths_file) as f:
            image_paths = f.readlines()

            for index, image_path in enumerate(tqdm(image_paths, desc="Processing Images")):
                with open(image_path.strip(), 'rb') as f:
                    encoded_image = base64.b64encode(f.read()).decode('utf-8')
                    orm.get_image(encoded_image, index)

    def download_and_prepare_images(self):
        """Download and extract images if they are not already present."""
        dataset_url = config.get("dataset_image_url")
        if not dataset_url:
            raise ValueError("Dataset URL not found in config.yaml")

        # Check if images are already extracted
        if self.dataset_path.exists() and any(self.dataset_path.iterdir()):
            print(f"Images already extracted in {self.dataset_path}")
            return

        # Download the dataset
        print("Downloading the dataset...")
        self.__download_dataset(dataset_url)

        # Extract the archive
        print("Extracting the tar file...")
        self.__extract_tarfile()

        # Save images to the database
        print("Saving images to the database...")
        self.__save_to_db()

        # Remove the archive after extraction
        self.dataset_archive_path.unlink()  # Use .unlink() to remove a Path object
        print("Archive deleted after extraction.")
