import _io
import base64
from io import BytesIO
from PIL import Image
import numpy as np

def singleton(cls):
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance

def image_to_based64(img):
    if isinstance(img, _io.BufferedReader):
        img_bytes = img.read()
    elif isinstance(img, bytes):
        img_bytes = img
    elif isinstance(img, np.ndarray):
        # If img is a numpy array, convert it to an image first
        img_pil = Image.fromarray(img)
        img_byte_io = BytesIO()
        img_pil.save(img_byte_io, format='JPEG')  # Save the numpy array as a JPEG image in memory
        img_byte_io.seek(0)  # Move the pointer back to the start of the byte stream
        img_bytes = img_byte_io.read()  # Get the bytes of the image
    else:
        raise ValueError("Input must be a bytes, file-like object, or numpy array")

    return f"data:image/jpeg;base64,{base64.b64encode(img_bytes).decode('utf-8')}"