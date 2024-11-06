import os
import torch
import logging
from PIL import Image
from transformers import AutoProcessor, AutoModelForZeroShotImageClassification
from typing import List
import faiss
import numpy as np

from .config import config
from misc import (singleton)

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@singleton
class Vectorizer:
    __instance = None

    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.processor = AutoProcessor.from_pretrained("zer0int/CLIP-GmP-ViT-L-14")
        self.model = AutoModelForZeroShotImageClassification.from_pretrained(config["clip_model"]).to(self.device)
        logger.info("CLIP processor and model initialized on device: %s", self.device)



    def __new__(cls):
        if cls.__instance is None:
            cls._instance = super(Vectorizer, cls).__new__(cls)
        return cls.__instance

    def compute_image_embeddings(self, images: List[np.array], **kwargs):

        if isinstance(images, List):
            images = [images]

        batch_size = kwargs.get('batch_size', 1)

        image_embeddings_list = []
        for i in range(0, len(images), batch_size):
            batch_images = images[i:i + batch_size]
            inputs = self.processor(images=batch_images, return_tensors="pt").to(self.device)
            with torch.no_grad():
                image_embedding = self.model.get_image_features(**inputs)
                image_embedding /= image_embedding.norm(dim=-1, keepdim=True)

            for i in range(image_embedding.size(0)):
                image_embeddings_list.append(image_embedding[i].cpu().numpy())

        if len(image_embeddings_list) == 1:
            return image_embeddings_list[0]

        return image_embeddings_list

    def compute_text_embedding(self, text):

        inputs = self.processor(text=text, return_tensors="pt").to(self.device)
        with torch.no_grad():
            text_embedding = self.model.get_text_features(**inputs)
            text_embedding /= text_embedding.norm(dim=-1, keepdim=True)

        return text_embedding

    def generate_and_store_image_embeddings(self, image_folder_path: str):
        """
        Generate embeddings for images in the specified folder and store them in a FAISS index.

        Parameters:
        - image_folder_path (str): Path of the folder containing images.

        Returns:
        - image_paths (list): List of image paths.
        """
        # Load image paths
        image_paths = load_image_paths(image_folder_path)
        num_images = len(image_paths)
        logger.info("Found %d images in folder: %s", num_images, image_folder_path)

        for idx, img_path in enumerate(image_paths, 1):
            # Load and preprocess the image
            image = Image.open(img_path).convert("RGB")
            embedding = self.compute_image_embeddings(image)

            # Add the embedding to FAISS
            self.faiss_index.add(embedding)

            # Log progress
            logger.info("Processed %d/%d images: %s", idx, num_images, img_path)

        # Save the FAISS index to a file
        faiss.write_index(self.faiss_index, self.faiss_index_path)
        logger.info("FAISS index saved to 'image_embeddings.index'.")

        logger.info("All embeddings generated and stored in FAISS index.")
        return image_paths


    def search_similar_images(self, query: str, top_k: int = 5):
        """
        Search for images most similar to a text query in the FAISS index.

        Parameters:
        - query (str): Text query for searching.
        - image_paths (list): List of image paths.
        - top_k (int): Number of most similar results to return.

        Returns:
        - similar_images (list): List of tuples (image path, distance) for the most similar images.
        """
        # Preprocess and encode the text query
        logger.info("Encoding query text: %s", query)
        embedding = self.compute_text_embedding(query)[0]

        # Search for top-k similar images in FAISS
        logger.info("Searching for top %d similar images.", top_k)
        distances, indices = self.faiss_index.search(embedding, top_k)

        return distances.reshape(-1), indices.reshape(-1)


def load_image_paths(image_directory: str):
    """
    Load image paths from a given directory and save them to image_paths.txt.

    Args:
    - image_directory (str): Path to the directory containing images.

    Returns:
    - List[str]: List of image paths.
    """
    image_paths = []
    for filename in os.listdir(image_directory):
        if filename.endswith(('.png', '.jpg', '.jpeg')):
            image_paths.append(os.path.join(image_directory, filename))

    logger.info("Loaded %d images from %s", len(image_paths), image_directory)

    # Save image paths to the file image_paths.txt
    with open("image_paths.txt", "w") as f:
        for path in image_paths:
            f.write(f"{path}\n")

    logger.info("Image paths saved to image_paths.txt.")
    return image_paths