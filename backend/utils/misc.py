import _io
import base64
from io import BytesIO
from PIL import Image
import numpy as np

def singleton(cls):
    """
    A decorator that ensures a class has only one instance. If an instance already exists,
    it returns that instance instead of creating a new one.

    Args:
        cls (type): The class to be instantiated as a singleton.

    Returns:
        object: The single instance of the specified class.
    """
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance

def image_to_based64(img) -> str:
    """
    Converts an image to a base64-encoded string suitable for embedding in HTML or other text-based formats.

    Args:
        img (_io.BufferedReader, bytes, or np.ndarray): The image to convert. 
            - Can be a file-like object, bytes, or a numpy array.
            - Numpy array images are converted to JPEG format.

    Returns:
        str: A base64-encoded string representing the image in JPEG format.
    
    Raises:
        ValueError: If the input type is not supported.
    """
    if isinstance(img, _io.BufferedReader):
        img_bytes = img.read()
    elif isinstance(img, bytes):
        img_bytes = img
    elif isinstance(img, np.ndarray):
        # Convert numpy array to a PIL image and then to bytes
        img_pil = Image.fromarray(img)
        img_byte_io = BytesIO()
        img_pil.save(img_byte_io, format=('JPEG' if img.shape[-1] == 3 else 'PNG'))  # Save the numpy array as a JPEG image in memory
        img_byte_io.seek(0)  # Move the pointer back to the start of the byte stream
        img_bytes = img_byte_io.read()  # Get the bytes of the image
    else:
        raise ValueError("Input must be a bytes, file-like object, or numpy array")

    return f"data:image/jpeg;base64,{base64.b64encode(img_bytes).decode('utf-8')}"
