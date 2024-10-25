from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from typing import List
import os
import base64
import random

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
IMAGES_FOLDER = os.path.join("H:/", "Desktop", "GoldenGate", "Images", "n02085620-Chihuahua") # To change

@app.get("/")
def home():
    return {"message": "Hello World!"}

# Endpoint pour obtenir les images pour une requête donnée
@app.get("/api/findImagesForQuery/{query}", response_model=List[str])
def find_images_for_query(query: str):
    # Vérifiez si le dossier existe
    if not os.path.isdir(IMAGES_FOLDER):
        raise HTTPException(status_code=404, detail="Image directory not found.")

    # Récupérez tous les fichiers dans le dossier d'images
    image_files = [f for f in os.listdir(IMAGES_FOLDER) if f.endswith(".jpg")]

    # Sélectionnez un sous-ensemble d'images de manière aléatoire
    random.shuffle(image_files)
    selected_images = image_files[:4]  # Retourner 4 images au hasard

    base64_images = []
    for filename in selected_images:
        image_path = os.path.join(IMAGES_FOLDER, filename)
        with open(image_path, "rb") as image_file:
            # Encode the image to base64
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            base64_images.append(f"data:image/jpeg;base64,{encoded_string}")

    return base64_images
