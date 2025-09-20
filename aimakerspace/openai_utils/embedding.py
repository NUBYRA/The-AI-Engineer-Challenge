import asyncio
import os
from typing import Iterable, List
from openai import AsyncOpenAI, OpenAI
from dotenv import load_dotenv


class EmbeddingModel:
    """Helper for generating embeddings via the OpenAI API."""

    def __init__(self, embeddings_model_name: str = "text-embedding-3-small", api_key: str = None):
        self.openai_api_key = api_key
        if self.openai_api_key is None:
            raise ValueError("OPENAI_API_KEY is not set and no api_key was provided.")

        self.embeddings_model_name = embeddings_model_name
        self.async_client = AsyncOpenAI(api_key=self.openai_api_key)
        self.client = OpenAI(api_key=self.openai_api_key)

    async def async_get_embeddings(self, list_of_text: Iterable[str]) -> List[List[float]]:
        """Return embeddings for ``list_of_text`` using the async client."""

        embedding_response = await self.async_client.embeddings.create(
            input=list(list_of_text), model=self.embeddings_model_name
        )

        return [item.embedding for item in embedding_response.data]

    async def async_get_embedding(self, text: str) -> List[float]:
        """Return an embedding for a single text using the async client."""

        embedding = await self.async_client.embeddings.create(
            input=text, model=self.embeddings_model_name
        )

        return embedding.data[0].embedding

    def get_embeddings(self, list_of_text: Iterable[str]) -> List[List[float]]:
        """Return embeddings for ``list_of_text`` using the sync client."""

        embedding_response = self.client.embeddings.create(
            input=list(list_of_text), model=self.embeddings_model_name
        )

        return [item.embedding for item in embedding_response.data]

    def get_embedding(self, text: str) -> List[float]:
        """Return an embedding for a single text using the sync client."""

        embedding = self.client.embeddings.create(
            input=text, model=self.embeddings_model_name
        )

        return embedding.data[0].embedding


if __name__ == "__main__":
    # Load .env file from project root (two levels up from this file)
    env_path = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
    load_dotenv(env_path, override=True)
    api_key = os.getenv("OPENAI_API_KEY")
    embedding_model = EmbeddingModel(api_key=api_key)
    print(asyncio.run(embedding_model.async_get_embedding("Hello, world!")))
    print(
        asyncio.run(
            embedding_model.async_get_embeddings(["Hello, world!", "Goodbye, world!"])
        )
    )
