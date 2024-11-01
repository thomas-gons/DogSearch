import os
import torch
import logging
from PIL import Image
from transformers import AutoProcessor, AutoModelForZeroShotImageClassification
import faiss

# Initialisation du logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialisation du modèle CLIP et du processeur avec le modèle `zer0int/CLIP-GmP-ViT-L-14`
device = "cuda" if torch.cuda.is_available() else "cpu"
processor = AutoProcessor.from_pretrained("zer0int/CLIP-GmP-ViT-L-14")
model = AutoModelForZeroShotImageClassification.from_pretrained("zer0int/CLIP-GmP-ViT-L-14").to(device)
logger.info("CLIP processor and model initialized on device: %s", device)

def load_image_paths(image_directory):
    """
    Charge les chemins d'images d'un répertoire donné et les sauvegarde dans image_paths.txt.
    
    Args:
    - image_directory (str): Chemin vers le répertoire contenant les images.

    Returns:
    - List[str]: Liste des chemins d'images.
    """
    image_paths = []
    for filename in os.listdir(image_directory):
        if filename.endswith(('.png', '.jpg', '.jpeg')):  # Ajouter d'autres extensions si nécessaire
            image_paths.append(os.path.join(image_directory, filename))
    
    logger.info("Loaded %d images from %s", len(image_paths), image_directory)

    # Sauvegarder les chemins d'images dans le fichier image_paths.txt
    with open("image_paths.txt", "w") as f:
        for path in image_paths:
            f.write(f"{path}\n")
    
    logger.info("Image paths saved to image_paths.txt.")
    return image_paths

# Fonction pour générer et stocker les embeddings d'images dans un index FAISS
def generate_and_store_image_embeddings(image_folder_path):
    """
    Génère les embeddings des images dans le dossier spécifié et les stocke dans un index FAISS.
    
    Parameters:
    - image_folder_path (str): Chemin du dossier contenant les images.
    
    Returns:
    - index (faiss.IndexFlatL2): Index FAISS contenant les embeddings d'images.
    - image_paths (list): Liste des chemins des images.
    """
    # Charger les chemins d'images
    image_paths = load_image_paths(image_folder_path)
    num_images = len(image_paths)
    logger.info("Found %d images in folder: %s", num_images, image_folder_path)

    # Initialisation de l'index FAISS (IndexFlatL2 pour la distance euclidienne)
    embedding_dim = model.config.projection_dim  # Dimension des embeddings CLIP
    index = faiss.IndexFlatL2(embedding_dim)

    for idx, img_path in enumerate(image_paths, 1):
        # Charger et prétraiter l'image
        image = Image.open(img_path).convert("RGB")
        inputs = processor(images=image, return_tensors="pt").to(device)
        
        # Générer l'embedding de l'image
        with torch.no_grad():
            image_embedding = model.get_image_features(**inputs)
            image_embedding /= image_embedding.norm(dim=-1, keepdim=True)  # Normalisation de l'embedding
        
        # Ajouter l'embedding à FAISS
        index.add(image_embedding.cpu().numpy())
        
        # Logging progress
        logger.info("Processed %d/%d images: %s", idx, num_images, img_path)
    
    # Sauvegarder l'index FAISS dans un fichier
    faiss.write_index(index, "image_embeddings.index")
    logger.info("FAISS index saved to 'image_embeddings.index'.")
    
    logger.info("All embeddings generated and stored in FAISS index.")
    return index, image_paths

# Fonction pour rechercher les top-k images similaires à une requête texte
def search_similar_images(query, index, image_paths, top_k=5):
    """
    Recherche les images les plus similaires à une requête texte dans l'index FAISS.
    
    Parameters:
    - query (str): Requête texte pour la recherche.
    - index (faiss.IndexFlatL2): Index FAISS contenant les embeddings d'images.
    - image_paths (list): Liste des chemins des images.
    - top_k (int): Nombre de résultats les plus similaires à retourner.
    
    Returns:
    - similar_images (list): Liste des tuples (chemin de l'image, distance) pour les images les plus similaires.
    """
    # Prétraiter et encoder la requête texte
    logger.info("Encoding query text: %s", query)
    inputs = processor(text=[query], return_tensors="pt").to(device)
    with torch.no_grad():
        query_embedding = model.get_text_features(**inputs)
        query_embedding /= query_embedding.norm(dim=-1, keepdim=True)  # Normalisation de l'embedding
    
    # Rechercher les top-k images similaires dans FAISS
    logger.info("Searching for top %d similar images.", top_k)
    distances, indices = index.search(query_embedding.cpu().numpy(), top_k)
    
    # Vérification de la validité des indices
    if len(image_paths) == 0:
        logger.warning("No images found or index is empty.")
        return []
    
    similar_images = []
    for idx, dist in zip(indices[0], distances[0]):
        if idx < len(image_paths):  # Vérification que l'index est valide
            similar_images.append((image_paths[idx], dist))
        else:
            logger.warning("Index %d out of range for image_paths of length %d", idx, len(image_paths))
    
    logger.info("Top %d similar images found for the query: %s", len(similar_images), query)
    for i, (path, dist) in enumerate(similar_images, 1):
        logger.info("Result %d: Image path: %s, Distance: %f", i, path, dist)
    
    return similar_images
