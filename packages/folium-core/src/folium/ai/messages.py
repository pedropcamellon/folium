"""OpenAI-compatible chat completion primitives."""

from typing import Any, Literal, TypedDict

from pydantic import BaseModel, Field


class OpenAIChatMessage(TypedDict):
    """A minimal OpenAI-compatible chat message."""

    role: Literal["system", "user"]
    content: str


def system_message(content: str) -> OpenAIChatMessage:
    """Create a system chat message."""
    return {"role": "system", "content": content}


def user_message(content: str) -> OpenAIChatMessage:
    """Create a user chat message."""
    return {"role": "user", "content": content}


class OpenAIChatCompletionMessage(BaseModel):
    """The text-bearing message returned by a chat completion choice."""

    content: str


class OpenAIChatCompletionChoice(BaseModel):
    """A minimal OpenAI-compatible chat completion choice."""

    message: OpenAIChatCompletionMessage


class OpenAIChatCompletion(BaseModel):
    """Validated minimal OpenAI-compatible chat completion response."""

    choices: list[OpenAIChatCompletionChoice] = Field(min_length=1)

    @property
    def content(self) -> str:
        """Return the first completion message content."""
        return self.choices[0].message.content


def parse_chat_completion(response: Any) -> OpenAIChatCompletion:
    """Validate and parse an OpenAI-compatible chat completion response."""
    return OpenAIChatCompletion.model_validate(response)
