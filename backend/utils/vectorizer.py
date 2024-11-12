import os
import torch
from PIL import Image
from transformers import AutoProcessor, AutoModelForZeroShotImageClassification
from typing import List
import numpy as np
from backend import logger, config
from backend.orm import ORM
from backend.utils.faiss_helper import FaissHelper
from backend.utils.misc import singleton, image_to_based64


@singleton
class Vectorizer:
    """
    A class for handling image and text embedding generation using a CLIP-based model.
    Includes functionality to store generated embeddings in a FAISS index.
    """

    def __init__(self):
        """
        Initializes the CLIP model and processor on the appropriate device (CUDA if available).
        """
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.processor = AutoProcessor.from_pretrained("zer0int/CLIP-GmP-ViT-L-14")
        self.model = AutoModelForZeroShotImageClassification.from_pretrained(config["clip_model"]).to(self.device)
        logger.info("CLIP processor and model initialized on device: %s", self.device)

    @property
    def embedding_dim(self) -> int:
        """
        Returns the dimensionality of the model's output embedding space.

        Returns:
            int: Dimension of the embedding vector.
        """
        return self.model.config.projection_dim

    def compute_image_embeddings(self, images: np.array, **kwargs) -> List[np.array]:
        """
        Computes embeddings for a batch of images.

        Args:
            images (np.array): Array of images to be processed.
            kwargs (dict): Optional parameters, e.g., batch_size.

        Returns:
            List[np.array]: List of computed embeddings for each image.
        """
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

    def compute_text_embedding(self, text: str) -> np.array:
        """
        Computes an embedding for a given text input.

        Args:
            text (str): Text to be converted into an embedding.

        Returns:
            np.array: Computed text embedding.
        """
        logger.info("Encoding query text: %s", text)
        inputs = self.processor(text=text, return_tensors="pt").to(self.device)
        with torch.no_grad():
            text_embedding = self.model.get_text_features(**inputs)
            text_embedding /= text_embedding.norm(dim=-1, keepdim=True)

        return text_embedding

    def generate_and_store_image_embeddings(self, faiss_helper: FaissHelper, image_folder_path: str) -> List[str]:
        """
        Generates embeddings for images in a specified folder and stores them in a FAISS index.

        Args:
            faiss_helper (FaissHelper): FAISS helper for storing embeddings.
            image_folder_path (str): Path of the folder containing images.

        Returns:
            List[str]: List of image paths processed.
        """
        image_paths = load_image_paths(image_folder_path)
        num_images = len(image_paths)
        logger.info("Found %d images in folder: %s", num_images, image_folder_path)

        for idx, img_path in enumerate(image_paths, 1):
            image = Image.open(img_path).convert("RGB")
            embedding = self.compute_image_embeddings([image])
            faiss_helper.add(embedding)
            logger.info("Processed %d/%d images: %s", idx, num_images, img_path)

        faiss_helper.save()
        logger.info("FAISS index saved to 'image_embeddings.index'.")
        logger.info("All embeddings generated and stored in FAISS index.")
        
        return image_paths

    def generate_and_store_embedding_from_user_image(self, images: List[dict], faiss_helper: FaissHelper, orm: ORM) -> None:
        """
        Generates and stores embeddings for user-uploaded images in a FAISS index.

        Args:
            images (List[dict]): List of image data dictionaries containing the 'data' and 'filename' keys.
            faiss_helper (FaissHelper): FAISS helper instance for adding embeddings.
            orm (ORM): ORM instance for storing image metadata.
        """
        batch = []
        last_faiss_index = faiss_helper.get_last_index()
        for i, image in enumerate(images):
            resized_image = np.array(image["data"].resize((224, 224)))

            # the model doesn't handle alpha channel
            rgb_image = resized_image[:, :, :3]
            batch.append(rgb_image)
            orm.add_image(image["filename"], image_to_based64(resized_image), last_faiss_index + i, 'user')

        kwargs = {"batch_size": len(batch)}
        embeddings = self.compute_image_embeddings(np.array(batch), **kwargs)
        faiss_helper.add(embeddings)
        logger.info("All uploaded images have been added to the database and FAISS index.")


def load_image_paths(image_directory: str) -> List[str]:
    """
    Loads image paths from a specified directory, saves them to a file, and returns the list.

    Args:
        image_directory (str): Path to the directory containing images.

    Returns:
        List[str]: List of image file paths.
    """
    image_paths = []
    for filename in os.listdir(image_directory):
        if filename.endswith(('.png', '.jpg', '.jpeg')):
            image_paths.append(os.path.join(image_directory, filename))

    logger.info("Loaded %d images from %s", len(image_paths), image_directory)

    with open("image_paths.txt", "w") as f:
        for path in image_paths:
            f.write(f"{path}\n")

    logger.info("Image paths saved to image_paths.txt.")
    return image_paths
