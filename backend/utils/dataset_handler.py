import tarfile
from pathlib import Path
import requests
from tqdm import tqdm
from backend import logger, config
from backend.orm import orm
from backend.utils.misc import singleton, image_to_based64


@singleton
class DatasetHandler:
    """
    A class to handle downloading, extracting, and saving image datasets for processing.
    """

    def __init__(self) -> None:
        """
        Initializes DatasetHandler with paths specified in the config file.
        """
        self.dataset_path = Path(config['dataset_path'])
        self.dataset_archive_path = Path(config['dataset_archive_path'])
        self.image_paths_file = Path(config['image_paths'])

    def __download_dataset(self, url: str):
        """
        Downloads the dataset archive from a specified URL and saves it to a designated location.

        Args:
            url (str): The URL from which to download the dataset archive.

        Raises:
            Exception: If the download fails due to HTTP errors.
        """
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            total_size = int(response.headers.get('content-length', 0))

            with open(self.dataset_archive_path, "wb") as f, tqdm(
                total=total_size, unit='B', unit_scale=True, desc=config['dataset_name']
            ) as pbar:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    pbar.update(len(chunk))

            logger.info(f"Download completed: {self.dataset_path}")
        else:
            raise Exception(f"Download failed. HTTP Status: {response.status_code}")

    def __extract_tarfile(self):
        """
        Extracts the downloaded tar archive to the target directory.
        """
        with tarfile.open(self.dataset_archive_path, "r") as tar:
            tar.extractall(path=self.dataset_path.parent)
        logger.info(f"Extraction completed at: {self.dataset_path}")

    def save_to_db(self):
        """
        Reads image paths from the file and saves each image to the database with encoding.
        """
        with open(self.image_paths_file) as f:
            image_paths = f.readlines()

            for index, img_partial_path in enumerate(
                tqdm(image_paths, total=len(image_paths), desc="Processing Images")
            ):
                img_path = self.dataset_path.parent / img_partial_path.strip()
                with open(img_path, 'rb') as img:
                    encoded_image = image_to_based64(img)
                    orm.add_image(
                        img_path.name, encoded_image, index, "database",
                        disable_logger_success=True
                    )

    def download_and_prepare_images(self):
        """
        Manages the dataset download, extraction, and preparation.
        - Checks if the images are already extracted and skips download if true.
        - Downloads the dataset archive if not already present.
        - Extracts the archive and saves each image to the database.
        - Deletes the archive file after successful extraction.
        """
        dataset_url = config["dataset_image_url"]

        # Check if images are already extracted
        if self.dataset_path.exists() and any(self.dataset_path.iterdir()):
            logger.info(f"Images already extracted in {self.dataset_path}")
            return

        if not self.dataset_archive_path.exists():
            # Download the dataset
            logger.info("Downloading the dataset...")
            self.__download_dataset(dataset_url)

        # Extract the archive
        logger.info("Extracting the tar file...")
        self.__extract_tarfile()

        # Save images to the database
        logger.info("Saving images to the database...")
        self.save_to_db()

        # Remove the archive after extraction
        self.dataset_archive_path.unlink()  # Use .unlink() to remove a Path object
        logger.info("Archive deleted after extraction.")
