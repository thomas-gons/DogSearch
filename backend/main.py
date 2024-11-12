from typing import List
from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from io import BytesIO
from PIL import Image

from backend import logger
from backend.orm import orm
from backend.utils.faiss_helper import FaissHelper
from backend.utils.dataset_handler import DatasetHandler
from backend.utils.vectorizer import Vectorizer


# Initialize and configure FastAPI
app = FastAPI()

# Initialize dataset handler and other components
dataset_handler = DatasetHandler()
vectorizer = Vectorizer()
faiss_helper = FaissHelper(vectorizer.embedding_dim)

# Set up CORS to allow requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Download and prepare images if necessary
logger.info("Downloading and preparing images if necessary.")
dataset_handler.download_and_prepare_images(orm.is_sample_db_built())


@app.get("/api/findImagesForQuery/{query}", response_model=List[str])
def find_images_for_query(query: str):
    """
    Endpoint to search and return images most similar to a given query.

    Args:
        query (str): The text query to search for similar images.

    Returns:
        List[str]: List of base64-encoded images that are most similar to the query.
    
    Raises:
        HTTPException: If no similar images are found, a 404 error is raised.
    """
    # Use FAISS to find the most similar images for the query
    embedding = vectorizer.compute_text_embedding(query)
    distances, indices = faiss_helper.search(embedding, k=4)
    
    if indices.size == 0:
        logger.warning("No similar images found for this query.")
        raise HTTPException(status_code=404, detail="No similar images found.")

    base64_images = []
    top_k_images = []

    # Retrieve and encode images from the FAISS index
    for i, indice in enumerate(indices):
        base64_image = orm.get_image_by_index(indice)
        base64_images.append(base64_image["data"])
        top_k_images.append([base64_image["filename"], distances[i]])

    logger.info(f"Top 4 similar images found for the query: {top_k_images}")
    logger.info("Selected images returned in base64.")

    return base64_images


@app.post("/api/uploadImages")
async def upload_images(files: List[UploadFile] = File(...)):
    """
    Endpoint to upload images and store their embeddings in the FAISS index.

    Args:
        files (List[UploadFile]): List of image files to upload.

    Returns:
        None
    """
    images = []

    # Read the uploaded images
    for file in files:
        img_bytes = await file.read()
        img = Image.open(BytesIO(img_bytes))
        images.append({
            "filename": file.filename,
            "data": img
        })

    # Generate and store image embeddings
    vectorizer.generate_and_store_embedding_from_user_image(images, faiss_helper, orm)


@app.delete("/api/removeUserImages")
def remove_user_images():
    """
    Endpoint to remove user-uploaded images from the FAISS index and the database.

    Returns:
        None
    """
    # Purge user data from the ORM and FAISS index
    indexes = orm.purge_user_data()
    faiss_helper.purge_user_data(indexes)
