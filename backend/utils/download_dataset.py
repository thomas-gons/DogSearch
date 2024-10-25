import requests
import os
from config import config
import tarfile


def download_dataset_file(url, path):
    filename = os.path.basename(url)
    response = requests.get(url)

    if response.status_code == 200:
        print("Download complete. Extracting files...")

        with open(filename, "wb") as file:
            file.write(response.content)
        
        with tarfile(filename) as tar:
            tar.extractall(path)
        

if __name__ == '__main__':
    download_dataset_file(config["dataset_image_url"], ".")
