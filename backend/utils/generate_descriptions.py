import os
import logging
import warnings
from PIL import Image
import torch
from transformers import BlipProcessor, BlipForConditionalGeneration

# Ignorer les warnings spécifiques
warnings.filterwarnings("ignore", category=UserWarning, module="transformers.generation.utils")

# Initialisation du logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Détection automatique du type de device (GPU si disponible, sinon CPU)
device = "cuda" if torch.cuda.is_available() else "cpu"

# Initialisation du processeur et du modèle avec les paramètres pré-entraînés
def initialize_blip_model():
    logger.info("Initializing BLIP processor and model.")
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
    model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base").to(device)
    model = model.half().to(device)
    logger.info("BLIP processor and model initialized.")
    return processor, model

# Génération des descriptions pour chaque image dans le dossier spécifié
def generate_descriptions(image_folder_path):
    logger.info(f"Generating descriptions for images in folder: {image_folder_path}")
    processor, model = initialize_blip_model()

    # Lister toutes les images dans le dossier
    image_files = [f for f in os.listdir(image_folder_path) if f.endswith('.jpg') or f.endswith('.png')]
    logger.info(f"Found {len(image_files)} images to process.")

    # Dictionnaire pour stocker les descriptions des images
    descriptions = {}

    for image_file in image_files:
        # Charger l'image
        img_path = os.path.join(image_folder_path, image_file)
        image = Image.open(img_path).convert("RGB")
        logger.debug(f"Processing image: {image_file}")

        # Prétraiter l'image pour le modèle
        inputs = processor(images=image, return_tensors="pt").to(device)

        # Générer la description
        with torch.no_grad():
            output = model.generate(**inputs, max_new_tokens=50)
        description = processor.decode(output[0], skip_special_tokens=True)
        
        # Afficher et stocker la description
        logger.info(f"Generated description for {image_file}: {description}")
        descriptions[image_file] = description

    logger.info("Image descriptions generation completed.")
    return descriptions
