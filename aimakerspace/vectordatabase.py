import asyncio
import os
import sys
from typing import Callable, Dict, Iterable, List, Optional, Tuple, Union
import numpy as np
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from aimakerspace.openai_utils.embedding import EmbeddingModel


def cosine_similarity(vector_a: np.ndarray, vector_b: np.ndarray) -> float:
    """Return the cosine similarity between two vectors."""

    norm_a = np.linalg.norm(vector_a)
    norm_b = np.linalg.norm(vector_b)
    if norm_a == 0 or norm_b == 0:
        return 0.0

    dot_product = np.dot(vector_a, vector_b)
    return float(dot_product / (norm_a * norm_b))


class VectorDatabase:
    """Minimal in-memory vector store backed by numpy arrays."""

    def __init__(self, embedding_model: Optional[EmbeddingModel] = None, api_key: str = None):
        self.vectors: Dict[str, np.ndarray] = {}
        self.api_key = api_key
        self.embedding_model = embedding_model or EmbeddingModel(api_key=api_key)

    def insert(self, key: str, vector: Iterable[float]) -> None:
        """Store ``vector`` so that it can be retrieved with ``key`` later on."""

        self.vectors[key] = np.asarray(vector, dtype=float)

    def search(
        self,
        query_vector: Iterable[float],
        k: int,
        distance_measure: Callable[[np.ndarray, np.ndarray], float] = cosine_similarity,
    ) -> List[Tuple[str, float]]:
        """Return the ``k`` vectors most similar to ``query_vector``."""

        if k <= 0:
            raise ValueError("k must be a positive integer")

        query = np.asarray(query_vector, dtype=float)
        scores = [
            (key, distance_measure(query, vector))
            for key, vector in self.vectors.items()
        ]
        scores.sort(key=lambda item: item[1], reverse=True)
        return scores[:k]

    def search_by_text(
        self,
        query_text: str,
        k: int,
        distance_measure: Callable[[np.ndarray, np.ndarray], float] = cosine_similarity,
        return_as_text: bool = False,
    ) -> Union[List[Tuple[str, float]], List[str]]:
        """Vector search using an embedding generated from ``query_text``."""

        query_vector = self.embedding_model.get_embedding(query_text)
        results = self.search(query_vector, k, distance_measure)
        if return_as_text:
            return [result[0] for result in results]
        return results

    def retrieve_from_key(self, key: str) -> Optional[np.ndarray]:
        """Return the stored vector for ``key`` if present."""

        return self.vectors.get(key)

    async def abuild_from_list(self, list_of_text: List[str]) -> "VectorDatabase":
        """Populate the vector store asynchronously from raw text snippets."""

        embeddings = await self.embedding_model.async_get_embeddings(list_of_text)
        for text, embedding in zip(list_of_text, embeddings):
            self.insert(text, embedding)
        return self


if __name__ == "__main__":
    list_of_text = [
        "I like to eat broccoli and bananas.",
        "I ate a banana and spinach smoothie for breakfast.",
        "Chinchillas and kittens are cute.",
        "My sister adopted a kitten yesterday.",
        "Look at this cute hamster munching on a piece of broccoli.",
    ]

    # Load .env file from project root (one level up from this file)
    env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    load_dotenv(env_path, override=True)
    api_key = os.getenv("OPENAI_API_KEY")

    vector_db = VectorDatabase(api_key=api_key)
    vector_db = asyncio.run(vector_db.abuild_from_list(list_of_text))
    k = 2

    searched_vector = vector_db.search_by_text("I think fruit is awesome!", k=k)
    print(f"Closest {k} vector(s):", searched_vector)

    retrieved_vector = vector_db.retrieve_from_key(
        "I like to eat broccoli and bananas."
    )
    print("Retrieved vector:", retrieved_vector)

    relevant_texts = vector_db.search_by_text(
        "I think fruit is awesome!", k=k, return_as_text=True
    )
    print(f"Closest {k} text(s):", relevant_texts)
