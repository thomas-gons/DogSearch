from pathlib import Path
import faiss
import numpy as np
from backend import config, logger
from backend.utils.misc import singleton


@singleton
class FaissHelper:
    """
    A helper class for managing and querying a Faiss index with vector embeddings.
    """

    def __init__(self, embedding_dim: int):
        """
        Initializes the Faiss index for embedding similarity searches.
        Loads an existing index if available, otherwise creates a new index.

        Args:
            embedding_dim (int): The dimension of the embedding vectors.
        """
        self.embedding_dim = embedding_dim
        self.index_path = config['faiss_index_path']
        readonly_faiss_index_path = config['readonly_faiss_index_path']

        if Path(self.index_path).exists():
            self.index = faiss.read_index(self.index_path)
        elif Path(readonly_faiss_index_path).exists():
            self.index = faiss.read_index(readonly_faiss_index_path)
        else:
            self.index = faiss.IndexFlatL2(self.embedding_dim)

    def __check_embeddings(self, embeddings: np.array) -> np.array:
        """
        Ensures embeddings have the correct dimension and are formatted as a 2D array.

        Args:
            embeddings (np.array): Embedding(s) to be checked.

        Raises:
            ValueError: If the embeddings' dimension does not match the Faiss index.

        Returns:
            np.array: Properly formatted 2D array of embeddings.
        """
        embeddings = np.array(embeddings, dtype=np.float32)

        if embeddings.ndim == 1:
            embeddings = embeddings.reshape(1, -1)

        if embeddings.shape[1] != self.embedding_dim:
            raise ValueError("The embedding should have the same dimension as that used in the Faiss index")

        return embeddings

    def add(self, embeddings: np.array) -> None:
        """
        Adds embeddings to the Faiss index after validating dimensions.

        Args:
            embeddings (np.array): Embedding vectors to be added to the index.
        """
        embeddings = self.__check_embeddings(embeddings)
        self.index.add(embeddings)

    def search(self, query_embedding: np.array, k: int = 5) -> (np.array, np.array):
        """
        Searches the index for the k most similar embeddings to the query embedding.

        Args:
            query_embedding (np.array): The query embedding to search against the index.
            k (int, optional): Number of closest neighbors to retrieve. Defaults to 5.

        Returns:
            tuple: A tuple containing:
                - distances (np.array): Array of distances to the closest neighbors.
                - indices (np.array): Array of indices for the closest neighbors.
        """
        query_embedding = self.__check_embeddings(query_embedding)
        distances, indices = self.index.search(query_embedding, k)

        return distances.reshape(-1), indices.reshape(-1)

    def get_last_index(self) -> int:
        """
        Retrieves the current total number of embeddings stored in the index.

        Returns:
            int: Total number of embeddings in the index.
        """
        return self.index.ntotal

    def save(self) -> None:
        """
        Saves the current state of the Faiss index to a file.
        """
        faiss.write_index(self.index, self.index_path)
        logger.info("Faiss index saved")

    def purge_user_data(self, indexes: list) -> None:
        """
        Removes embeddings from the index based on provided indices.

        Args:
            indexes (list): List of indices for embeddings to be removed.
        """
        if indexes:
            embedding_indexes_array = np.array(indexes, dtype=np.int64)
            self.index.remove_ids(faiss.IDSelectorArray(embedding_indexes_array))
