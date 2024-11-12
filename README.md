# DogSearch: Image Generation and Similarity Search

This project is a comprehensive application that integrates **Deep Learning**, **Image-Based Processing**, and **Natural Language Processing (NLP)**, developed by engineering students specializing in Artificial Intelligence at CY TECH.

## Project Goals

The goal of this project is to create an interactive platform that enables the following functionalities:

- **Image Similarity Search:** Search for images that are most similar to a given input image, based on feature embeddings and similarity search in a vector space.
- **Text-to-Image Search:** Perform a search for images corresponding to a given textual query, using advanced models to compute the similarity between text and images.
- **Image Upload and Search:** Allow users to upload their own images, store embeddings, and search for similar images in the database.
- **Image Description Generation:** Use advanced models such as CLIP to generate descriptions from images provided by the user.

## Technologies Used

- **CLIP Model:** A vision-language model that connects images and text in a shared embedding space. It is used for generating textual descriptions of images and for searching similar images based on text.
- **Faiss:** A high-performance library for similarity search, used to index and quickly find the most similar images based on embeddings.
- **FastAPI:** A modern, fast web framework for building APIs in Python, used for backend development.
- **SQLAlchemy (ORM):** Used for interacting with the SQLite database to store image metadata and embeddings.
- **Pillow (PIL):** Python Imaging Library used for processing and handling image uploads.
- **JavaScript (Vue.js):** Used for the frontend interface to interact with the backend API and display results.

## Project Structure

### Backend

The backend is built using FastAPI and provides the following features:

- **Image Upload:** Users can upload images, and their embeddings are stored in the database.
- **Text Search:** The API allows querying for images that match a given textual description.
- **Image Search:** The API provides endpoints to find similar images based on a given image.
- **Database Integration:** SQLite is used to store image metadata (filename, embedding, origin).
- **Faiss Integration:** Used to index image embeddings and efficiently search for similar images.

### Frontend

The frontend is built using Vue.js and provides a user-friendly interface for interacting with the backend.

- **Image Search Interface:** Allows users to input a text query to search for similar images.
- **Image Upload:** Users can upload images to generate embeddings and store them for future search.
- **Results Display:** Displays the images most similar to the search query or uploaded image.

## How to Run the Project

### Backend

The backend is built using FastAPI and Uvicorn. To run the backend:

1) **Create** a virtual environment and install dependencies (inside `backend/` repository):
    ```bash
    pip install -r requirements.txt
    ```

2) **Run** the FastAPI server (from root project repository):
    ```bash
    uvicorn backend.main:app --host 0.0.0.0 --port 8000
    ```

The API will be available at http://localhost:8000. The backend includes several endpoints for image search, uploading images, and removing images.

### Frontend

To set up and run the frontend:

1) **Install** dependencies using npm (inside `frontend/` repository):
    ```bash
    npm install
    ```

2) **Start** the development server (inside `frontend/` repository):
    ```bash
    npm run dev
    ```

The frontend will be available at http://localhost:8080. It will allow you to interact with the backend by uploading images or entering text queries.

## Endpoints

### `/api/findImagesForQuery/{query}`

- **Method:** GET
- **Description:** Search for images most similar to a given query (text).
- **Parameters:**
    - *query:* The search query (string).
- **Response:** List of base64-encoded images most similar to the query.

### `/api/uploadImages`
- **Method:** POST
- **Description:** Upload images and store them in the database.
- **Parameters:**
    - *files:* A list of images to be uploaded.
- **Response:** Status message or error.

### `/api/removeUserImages`

- **Method:** DELETE
- **Description:** Remove all images uploaded by the user and their embeddings.
- **Response:** Success or error message.

## Team Members

- **Thomas GONS** - 3rd-year engineering student, CY TECH - AI
- **Louis-Alexandre LAGUET** - 3rd-year engineering student, CY TECH - AI

## License

This project is licensed under the MIT License.
