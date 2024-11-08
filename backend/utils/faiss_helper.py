from pathlib import Path

import faiss
import numpy as np

from backend import config, logger
from backend.utils.misc import (singleton)


@singleton
class FaissHelper:

    def __init__(self, embedding_dim):
        self.embedding_dim = embedding_dim
        self.index_path = config['faiss_index_path']
        readonly_faiss_index_path = config['readonly_faiss_index_path']
        if Path(self.index_path).exists():
            self.index = faiss.read_index(self.index_path)
        elif Path(readonly_faiss_index_path).exists():
            self.index = faiss.read_index(readonly_faiss_index_path)
        else:
            self.index = faiss.IndexFlatL2(self.embedding_dim)

    def __check_embeddings(self, embeddings):
        embeddings = np.array(embeddings, dtype=np.float32)

        if embeddings.ndim == 1:
            embeddings = embeddings.reshape(1, -1)

        if embeddings.shape[1] != self.embedding_dim:
            raise ValueError("The embedding should have the same dimension as that used in the faiss index")

        return embeddings

    def add(self, embeddings):
        embeddings = self.__check_embeddings(embeddings)
        self.index.add(embeddings)

    def search(self, query_embedding: np.array, k: int = 5) -> (np.array, np.array):
        query_embedding = self.__check_embeddings(query_embedding)
        distances, indices = self.index.search(query_embedding, k)

        return distances.reshape(-1), indices.reshape(-1)

    def get_last_index(self):
        return self.index.ntotal

    def save(self) -> None:
        faiss.write_index(self.index, self.index_path)
        logger.info("Faiss index saved")

    def purge_user_data(self, indexes):
        if indexes:
            embedding_indexes_array = np.array(indexes, dtype=np.int64)
            self.index.remove_ids(faiss.IDSelectorArray(embedding_indexes_array))

