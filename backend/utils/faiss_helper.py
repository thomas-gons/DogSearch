import faiss
import numpy as np
from pathlib import Path

from config import config
from misc import (singleton)


@singleton
class FaissHelper:
    def __init__(self, embedding_dim):
        self.embedding_dim = embedding_dim
        self.index_path = config['faiss_index_path']
        if Path(self.index_path).exists():
            self.index = faiss.read_index(self.index_path)
            self.do_backup()
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

    def search(self, query_embedding, k=5):
        query_embedding = self.__check_embeddings(query_embedding)
        distances, indices = self.index.search(query_embedding, k)

        return distances.reshape(-1), indices.reshape(-1)

    def save(self):
        faiss.write_index(self.index, self.index_path)


    def do_backup(self):
        faiss.write_index(self.index, f"{self.index_path}.bak")
