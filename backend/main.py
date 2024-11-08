from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend import logger

from orm import orm
from utils.faiss_helper import FaissHelper
from utils.dataset_handler import DatasetHandler
from utils.vectorizer import Vectorizer


# Initialize and configure FastAPI
app = FastAPI()

dataset_handler = DatasetHandler()

# Set up CORS to allow requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Download and prepare images if needed
logger.info("Downloading and preparing images if necessary.")
dataset_handler.download_and_prepare_images()
vectorizer = Vectorizer()
faiss_helper = FaissHelper(vectorizer.embedding_dim)

# Define an endpoint for searching similar images
@app.get("/api/findImagesForQuery/{query}", response_model=List[str])
def find_images_for_query(query: str):
    """Endpoint to search and return images most similar to a given query."""

    # Use FAISS to find the most similar images for the query
    embedding = vectorizer.compute_text_embedding(query)
    distances, indices = faiss_helper.search(embedding, k=4)
    if indices.size == 0:
        logger.warning("No similar images found for this query.")
        raise HTTPException(status_code=404, detail="No similar images found.")

    base64_images = []
    top_k_images = []
    for i, indice in enumerate(indices):
        # Use ORM to retrieve the image from the FAISS index, using the appropriate index
        base64_image = orm.get_image_by_index(indice)
        base64_images.append(base64_image["data"])
        top_k_images.append([base64_image["filename"], distances[i]])

    logger.info(f"Top 4 similar images found for the query: {top_k_images}")

    logger.info("Selected images returned in base64.")
    return base64_images


from fastapi import File, UploadFile
from io import BytesIO
from PIL import Image


@app.post("/api/uploadImages")
async def upload_images(files: List[UploadFile] = File(...)):
    images = []
    for file in files:
        img_bytes = await file.read()
        img = Image.open(BytesIO(img_bytes))

        images.append({
            "filename": file.filename,
            "data": img
        })

    vectorizer.generate_and_store_embedding_from_user_image(images, faiss_helper, orm)


@app.delete("/api/removeUserImages")
def remove_user_images():
    indexes = orm.purge_user_data()
    faiss_helper.purge_user_data(indexes)
