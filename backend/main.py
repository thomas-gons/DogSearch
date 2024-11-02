import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

import base64
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from utils.vectorize import generate_and_store_image_embeddings, search_similar_images
import faiss  # Assurez-vous d'importer FAISS

# Initialisation du logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Configuration de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Chemin vers le dossier des images et le fichier d'index FAISS
IMAGES_FOLDER = os.path.join("..", "Images")
INDEX_FILE = "index.faiss"  # Nom du fichier d'index FAISS

# Vérification si l'index existe déjà et chargement ou création
if os.path.exists(INDEX_FILE):
    logger.info(f"Loading FAISS index from {INDEX_FILE}.")
    index = faiss.read_index(INDEX_FILE)

    # Chargement des chemins d'image à partir d'un fichier
    if os.path.exists("image_paths.txt"):
        with open("image_paths.txt", "r") as f:
            image_paths = [line.strip() for line in f.readlines()]
    else:
        logger.error("Image paths file not found.")
        raise HTTPException(status_code=500, detail="Image paths file not found.")

else:
    logger.info("Generating and storing image embeddings in FAISS.")
    index, image_paths = generate_and_store_image_embeddings(IMAGES_FOLDER)

    # Sauvegarde de l'index
    faiss.write_index(index, INDEX_FILE)
    logger.info("Image embeddings generated and stored successfully.")

    # Sauvegarde des chemins d'image dans un fichier
    with open("image_paths.txt", "w") as f:
        for path in image_paths:
            f.write(f"{path}\n")
    logger.info("Image paths saved to 'image_paths.txt'.")

# Endpoint pour obtenir les images en fonction de la similarité avec la requête
@app.get("/api/findImagesForQuery/{query}", response_model=List[str])
def find_images_for_query(query: str):
    logger.info(f"Received query: {query}")

    # Vérifier si le dossier existe
    if not os.path.isdir(IMAGES_FOLDER):
        logger.error(f"Image directory not found at path: {IMAGES_FOLDER}")
        raise HTTPException(status_code=404, detail="Image directory not found.")
    
    # Utiliser FAISS pour trouver les images les plus similaires à la requête
    top_k_images = search_similar_images(query, index, image_paths, top_k=4)

    # Vérification si des images ont été trouvées
    if not top_k_images:
        logger.warning("No similar images found for the query.")
        raise HTTPException(status_code=404, detail="No similar images found.")

    logger.info(f"Top 4 images found for the query: {top_k_images}")

    # Conversion des images sélectionnées en base64
    base64_images = []
    for image_path, _ in top_k_images:
        with open(image_path, "rb") as image_file:
            # Encoder l'image en base64
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            base64_images.append(f"data:image/jpeg;base64,{encoded_string}")
        logger.debug(f"Encoded image: {image_path}")

    logger.info("Returning selected images as base64.")
    return base64_images
