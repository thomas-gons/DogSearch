import os
import base64
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from sentence_transformers import SentenceTransformer, util
from utils.generate_descriptions import generate_descriptions

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

# Chemin vers le dossier des images
IMAGES_FOLDER = os.path.join("H:/", "Desktop", "GoldenGate", "Images", "n02085620-Chihuahua")  # Adapter ce chemin si besoin

# Générer les descriptions des images
logger.info("Starting to generate descriptions for images in the folder.")
descriptions = generate_descriptions(IMAGES_FOLDER)
logger.info("Image descriptions generated successfully.")

# Charger le modèle Sentence Transformer pour calculer la similarité sémantique
logger.info("Loading the Sentence Transformer model.")
sentence_model = SentenceTransformer('all-MiniLM-L6-v2')

# Encoder les descriptions générées par BLIP
logger.info("Encoding image descriptions.")
encoded_descriptions = {img_file: sentence_model.encode(desc) for img_file, desc in descriptions.items()}
logger.info("Image descriptions encoded successfully.")

# Endpoint pour obtenir les images en fonction de la similarité avec la requête
@app.get("/api/findImagesForQuery/{query}", response_model=List[str])
def find_images_for_query(query: str):
    logger.info(f"Received query: {query}")

    # Vérifier si le dossier existe
    if not os.path.isdir(IMAGES_FOLDER):
        logger.error(f"Image directory not found at path: {IMAGES_FOLDER}")
        raise HTTPException(status_code=404, detail="Image directory not found.")
    
    # Encoder la requête de l'utilisateur
    query_embedding = sentence_model.encode(query)
    logger.info("Query encoded successfully.")

    # Calculer la similarité cosinus entre la requête et chaque description d'image
    similarity_scores = {
        img_file: util.cos_sim(query_embedding, desc_embedding).item()
        for img_file, desc_embedding in encoded_descriptions.items()
    }
    logger.info("Similarity scores computed.")

    # Trier les images par similarité décroissante et sélectionner les 4 meilleures
    top_images = sorted(similarity_scores, key=similarity_scores.get, reverse=True)[:4]
    logger.info(f"Top 4 images selected: {top_images}")

    # Conversion des images sélectionnées en base64
    base64_images = []
    for filename in top_images:
        image_path = os.path.join(IMAGES_FOLDER, filename)
        with open(image_path, "rb") as image_file:
            # Encoder l'image en base64
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            base64_images.append(f"data:image/jpeg;base64,{encoded_string}")
        logger.debug(f"Encoded image: {filename}")

    logger.info("Returning selected images as base64.")
    return base64_images
