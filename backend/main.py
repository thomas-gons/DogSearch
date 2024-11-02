import os
import base64
import logging
import faiss
from typing import List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from utils.vectorize import generate_and_store_image_embeddings, search_similar_images
from utils.dataset_handler import DatasetHandler
from orm import orm
from utils.config import config

# Configure environment to prevent conflicts with certain libraries
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
# Logger setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize and configure FastAPI
app = FastAPI()

# Initialize a DatasetHandler instance
dataset = DatasetHandler()

# Set up CORS to allow requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Paths for image directories and files
INDEX_FILE = Path(config['faiss_index_path'])
IMAGE_PATH_FILE = Path("resources") / "image_paths.txt"

# Download and prepare images if needed
logger.info("Downloading and preparing images if necessary.")
dataset.download_and_prepare_images()

# Initialize or load FAISS index
if INDEX_FILE.exists():
    # Load existing FAISS index
    logger.info(f"Loading FAISS index from {INDEX_FILE}.")
    index = faiss.read_index(str(INDEX_FILE))

    # Load image paths from text file
    if IMAGE_PATH_FILE.exists():
        with open(IMAGE_PATH_FILE, "r") as f:
            image_paths = [line.strip() for line in f.readlines()]
    else:
        logger.error("Image paths file not found.")
        raise HTTPException(status_code=500, detail="Image paths file not found.")
else:
    # Generate and store FAISS index if it does not exist
    logger.info("Generating and storing image embeddings in FAISS.")
    index, image_paths = generate_and_store_image_embeddings(config['dataset_path'])

    # Save FAISS index to disk
    faiss.write_index(index, str(INDEX_FILE))
    logger.info("Image embeddings generated and stored successfully.")

    # Save image paths to a text file
    with open(IMAGE_PATH_FILE, "w") as f:
        for path in image_paths:
            f.write(f"{path}\n")
    logger.info("Image paths saved to 'image_paths.txt'.")

# Define an endpoint for searching similar images
@app.get("/api/findImagesForQuery/{query}", response_model=List[str])
def find_images_for_query(query: str):
    """Endpoint to search and return images most similar to a given query."""
    
    logger.info(f"Received query for similar image search: {query}")

    # Use FAISS to find the most similar images for the query
    distances, top_k_indices = search_similar_images(query, index, image_paths, top_k=4)

    # Check if similar images were found
    if top_k_indices.size == 0:
        logger.warning("No similar images found for this query.")
        raise HTTPException(status_code=404, detail="No similar images found.")


    base64_images = []
    top_k_images = []
    for i, indice in enumerate(top_k_indices):
        # Use ORM to retrieve the image from the FAISS index, using the appropriate index
        base64_image = orm.get_image_by_index(indice)
        base64_images.append(base64_image["data"])
        top_k_images.append([base64_image["filename"], distances[i]])

    logger.info(f"Top 4 similar images found for the query: {top_k_images}")

    logger.info("Selected images returned in base64.")
    return base64_images
