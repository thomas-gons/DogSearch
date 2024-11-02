import os
import torch
import logging
from PIL import Image
from transformers import AutoProcessor, AutoModelForZeroShotImageClassification
import faiss

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the CLIP model and processor using the model `zer0int/CLIP-GmP-ViT-L-14`
device = "cuda" if torch.cuda.is_available() else "cpu"
processor = AutoProcessor.from_pretrained("zer0int/CLIP-GmP-ViT-L-14")
model = AutoModelForZeroShotImageClassification.from_pretrained("zer0int/CLIP-GmP-ViT-L-14").to(device)
logger.info("CLIP processor and model initialized on device: %s", device)

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

def generate_and_store_image_embeddings(image_folder_path: str):
    """
    Generate embeddings for images in the specified folder and store them in a FAISS index.
    
    Parameters:
    - image_folder_path (str): Path of the folder containing images.
    
    Returns:
    - index (faiss.IndexFlatL2): FAISS index containing image embeddings.
    - image_paths (list): List of image paths.
    """
    # Load image paths
    image_paths = load_image_paths(image_folder_path)
    num_images = len(image_paths)
    logger.info("Found %d images in folder: %s", num_images, image_folder_path)

    # Initialize the FAISS index (IndexFlatL2 for Euclidean distance)
    embedding_dim = model.config.projection_dim
    index = faiss.IndexFlatL2(embedding_dim)

    for idx, img_path in enumerate(image_paths, 1):
        # Load and preprocess the image
        image = Image.open(img_path).convert("RGB")
        inputs = processor(images=image, return_tensors="pt").to(device)
        
        # Generate the image embedding
        with torch.no_grad():
            image_embedding = model.get_image_features(**inputs)
            image_embedding /= image_embedding.norm(dim=-1, keepdim=True)
        
        # Add the embedding to FAISS
        index.add(image_embedding.cpu().numpy())
        
        # Log progress
        logger.info("Processed %d/%d images: %s", idx, num_images, img_path)
    
    # Save the FAISS index to a file
    faiss.write_index(index, "image_embeddings.index")
    logger.info("FAISS index saved to 'image_embeddings.index'.")
    
    logger.info("All embeddings generated and stored in FAISS index.")
    return index, image_paths

def search_similar_images(query: str, index, image_paths: list, top_k: int = 5):
    """
    Search for images most similar to a text query in the FAISS index.
    
    Parameters:
    - query (str): Text query for searching.
    - index (faiss.IndexFlatL2): FAISS index containing image embeddings.
    - image_paths (list): List of image paths.
    - top_k (int): Number of most similar results to return.
    
    Returns:
    - similar_images (list): List of tuples (image path, distance) for the most similar images.
    """
    # Preprocess and encode the text query
    logger.info("Encoding query text: %s", query)
    inputs = processor(text=[query], return_tensors="pt").to(device)
    with torch.no_grad():
        query_embedding = model.get_text_features(**inputs)
        query_embedding /= query_embedding.norm(dim=-1, keepdim=True)
    
    # Search for top-k similar images in FAISS
    logger.info("Searching for top %d similar images.", top_k)
    distances, indices = index.search(query_embedding.cpu().numpy(), top_k)
    
    return distances.reshape(-1), indices.reshape(-1)
