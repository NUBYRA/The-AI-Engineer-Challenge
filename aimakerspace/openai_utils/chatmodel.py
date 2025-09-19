import os
from typing import Any, AsyncIterator, Iterable, List, MutableMapping
from dotenv import load_dotenv
from openai import AsyncOpenAI, OpenAI

load_dotenv()

ChatMessage = MutableMapping[str, Any]


class ChatOpenAI:
    """Thin wrapper around the OpenAI chat completion APIs."""

    def __init__(self, model_name: str = "gpt-4o-mini", api_key: str = None):
        """
        Initialize the ChatOpenAI instance.

        Args:
            model_name (str): The name of the OpenAI chat model to use.
            api_key (str, optional): The OpenAI API key. If not provided, will attempt to load from environment variable OPENAI_API_KEY.

        Raises:
            ValueError: If no API key is provided and OPENAI_API_KEY is not set in the environment.
        """
        self.model_name = model_name
        # Prefer explicit api_key argument, fallback to environment variable
        self.openai_api_key = api_key or os.getenv("OPENAI_API_KEY")
        if self.openai_api_key is None:
            raise ValueError("OPENAI_API_KEY is not set and no api_key was provided.")

        self._client = OpenAI(api_key=self.openai_api_key)
        self._async_client = AsyncOpenAI(api_key=self.openai_api_key)

    def run(
        self,
        messages: Iterable[ChatMessage],
        text_only: bool = True,
        **kwargs: Any,
    ) -> Any:
        """Execute a chat completion request.

        ``messages`` must be an iterable of ``{"role": ..., "content": ...}``
        dictionaries. When ``text_only`` is ``True`` (the default) only the
        completion text is returned; otherwise the full response object is
        provided.
        """

        message_list = self._coerce_messages(messages)
        response = self._client.chat.completions.create(
            model=self.model_name, messages=message_list, **kwargs
        )

        if text_only:
            return response.choices[0].message.content

        return response

    async def astream(
        self, messages: Iterable[ChatMessage], **kwargs: Any
    ) -> AsyncIterator[str]:
        """Yield streaming completion chunks as they arrive from the API."""

        message_list = self._coerce_messages(messages)
        stream = self._async_client.chat.completions.create(
            model=self.model_name, messages=message_list, stream=True, **kwargs
        )

        async for chunk in stream:
            content = chunk.choices[0].delta.content
            if content is not None:
                yield content

    def _coerce_messages(self, messages: Iterable[ChatMessage]) -> List[ChatMessage]:
        if isinstance(messages, list):
            return messages
        return list(messages)
