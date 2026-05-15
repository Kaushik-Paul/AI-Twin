import json
import os
from collections.abc import AsyncIterator
from dataclasses import replace
from pathlib import Path
from typing import Any

import litellm
from agents import Model
from agents.extensions.models.litellm_model import LitellmModel
from dotenv import load_dotenv
from pydantic import BaseModel

from . import constants

load_dotenv(override=True)
load_dotenv(Path(__file__).resolve().parents[2] / ".env", override=True)

DEFAULT_OPENROUTER_MODEL = "google/gemini-2.5-flash-lite"
DEFAULT_OPENCODE_GO_MODEL = "deepseek-v4-flash"


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def _env_required(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def use_openrouter() -> bool:
    return _env_bool("USE_OPENROUTER", default=False)


def use_evaluation_openrouter() -> bool:
    return _env_bool("USE_EVALUATION_OPENROUTER", default=False)


def active_chat_model_name() -> str:
    if use_openrouter():
        return os.getenv("DEFAULT_MODEL_NAME", DEFAULT_OPENROUTER_MODEL)
    return os.getenv("OPENCODE_GO_MODEL", DEFAULT_OPENCODE_GO_MODEL)


def active_evaluation_model_name() -> str:
    if use_evaluation_openrouter():
        return os.getenv("EVALUATION_MODEL_NAME", DEFAULT_OPENROUTER_MODEL)
    return os.getenv("OPENCODE_GO_MODEL", DEFAULT_OPENCODE_GO_MODEL)


def _opencode_go_model_name(model: str, api_style: str) -> str:
    return f"{api_style}/{model}"


def _disable_opencode_go_thinking() -> bool:
    return _env_bool("OPENCODE_GO_DISABLE_THINKING", default=True)


def _with_opencode_model_settings(
    args: tuple[Any, ...], kwargs: dict[str, Any], api_style: str
) -> tuple[tuple[Any, ...], dict[str, Any]]:
    if api_style != "openai" or not _disable_opencode_go_thinking():
        return args, kwargs

    if "model_settings" in kwargs:
        model_settings = kwargs["model_settings"]
        extra_body = {
            **(model_settings.extra_body or {}),
            "extra_body": {
                **(model_settings.extra_body or {}).get("extra_body", {}),
                "thinking": {"type": "disabled"},
            },
        }
        kwargs = {
            **kwargs,
            "model_settings": replace(
                model_settings, extra_body=extra_body
            ),
        }
        return args, kwargs

    model_settings_index = 2
    if len(args) <= model_settings_index:
        return args, kwargs

    model_settings = args[model_settings_index]
    extra_body = {
        **(model_settings.extra_body or {}),
        "extra_body": {
            **(model_settings.extra_body or {}).get("extra_body", {}),
            "thinking": {"type": "disabled"},
        },
    }
    updated_args = list(args)
    updated_args[model_settings_index] = replace(
        model_settings, extra_body=extra_body
    )
    return tuple(updated_args), kwargs


class OpenCodeGoModel(Model):
    _api_style_cache: dict[str, str] = {}

    def __init__(
        self, model: str, api_key: str | None, api_style: str = "auto"
    ) -> None:
        self.model = model
        self.api_style = api_style.strip().lower()
        if self.api_style not in {"auto", "openai", "anthropic"}:
            raise ValueError("OPENCODE_GO_API_STYLE must be auto, openai, or anthropic")
        self._clients = {
            "openai": LitellmModel(
                model=_opencode_go_model_name(model, "openai"),
                base_url=constants.OPENCODE_GO_OPENAI_BASE_URL,
                api_key=api_key,
            ),
            "anthropic": LitellmModel(
                model=_opencode_go_model_name(model, "anthropic"),
                base_url=constants.OPENCODE_GO_ANTHROPIC_BASE_URL,
                api_key=api_key,
            ),
        }
        self._active_api_style = self._initial_api_style()

    def _initial_api_style(self) -> str:
        if self.api_style != "auto":
            return self.api_style
        return self._api_style_cache.get(self.model, "openai")

    def _alternate_api_style(self) -> str:
        return "anthropic" if self._active_api_style == "openai" else "openai"

    async def get_response(self, *args: Any, **kwargs: Any) -> Any:
        try:
            call_args, call_kwargs = _with_opencode_model_settings(
                args, kwargs, self._active_api_style
            )
            response = await self._clients[self._active_api_style].get_response(
                *call_args, **call_kwargs
            )
            self._api_style_cache[self.model] = self._active_api_style
            return response
        except Exception as first_error:
            if self.api_style != "auto":
                raise
            first_api_style = self._active_api_style
            self._active_api_style = self._alternate_api_style()
            try:
                call_args, call_kwargs = _with_opencode_model_settings(
                    args, kwargs, self._active_api_style
                )
                response = await self._clients[self._active_api_style].get_response(
                    *call_args, **call_kwargs
                )
                self._api_style_cache[self.model] = self._active_api_style
                return response
            except Exception as second_error:
                raise RuntimeError(
                    f"OpenCode Go model '{self.model}' failed with both "
                    f"{first_api_style} and {self._active_api_style} API styles. "
                    f"First error: {first_error}"
                ) from second_error

    def stream_response(self, *args: Any, **kwargs: Any) -> AsyncIterator[Any]:
        async def stream() -> AsyncIterator[Any]:
            try:
                stream_args, stream_kwargs = _with_opencode_model_settings(
                    args, kwargs, self._active_api_style
                )
                async for chunk in self._clients[
                    self._active_api_style
                ].stream_response(*stream_args, **stream_kwargs):
                    yield chunk
                self._api_style_cache[self.model] = self._active_api_style
            except Exception:
                if self.api_style != "auto":
                    raise
                self._active_api_style = self._alternate_api_style()
                stream_args, stream_kwargs = _with_opencode_model_settings(
                    args, kwargs, self._active_api_style
                )
                async for chunk in self._clients[
                    self._active_api_style
                ].stream_response(*stream_args, **stream_kwargs):
                    yield chunk
                self._api_style_cache[self.model] = self._active_api_style

        return stream()


def create_agent_model() -> Model:
    if use_openrouter():
        model_name = os.getenv("DEFAULT_MODEL_NAME", DEFAULT_OPENROUTER_MODEL)
        return LitellmModel(model="openrouter/" + model_name)

    return OpenCodeGoModel(
        model=active_chat_model_name(),
        api_key=os.getenv("OPENCODE_GO_API_KEY"),
        api_style=os.getenv("OPENCODE_GO_API_STYLE", "auto"),
    )


def opencode_go_completion(messages: list[dict[str, str]], model: str) -> Any:
    api_key = _env_required("OPENCODE_GO_API_KEY")
    api_style = os.getenv("OPENCODE_GO_API_STYLE", "auto").strip().lower()
    if api_style not in {"auto", "openai", "anthropic"}:
        raise ValueError("OPENCODE_GO_API_STYLE must be auto, openai, or anthropic")

    api_styles = ["openai", "anthropic"] if api_style == "auto" else [api_style]
    first_error: Exception | None = None

    for style in api_styles:
        try:
            extra_kwargs = {}
            if style == "openai" and _disable_opencode_go_thinking():
                extra_kwargs["extra_body"] = {"thinking": {"type": "disabled"}}

            return litellm.completion(
                model=_opencode_go_model_name(model, style),
                messages=messages,
                api_key=api_key,
                base_url=(
                    constants.OPENCODE_GO_OPENAI_BASE_URL
                    if style == "openai"
                    else constants.OPENCODE_GO_ANTHROPIC_BASE_URL
                ),
                **extra_kwargs,
            )
        except Exception as error:
            if first_error is None:
                first_error = error
            if api_style != "auto":
                raise

    raise RuntimeError(
        f"OpenCode Go model '{model}' failed with both OpenAI-compatible and "
        f"Anthropic API styles. First error: {first_error}"
    )


def parse_json_model_response(content: str, schema: type[BaseModel]) -> BaseModel:
    try:
        return schema.model_validate_json(content)
    except Exception:
        stripped = content.strip()
        if stripped.startswith("```"):
            stripped = stripped.removeprefix("```json").removeprefix("```").strip()
            stripped = stripped.removesuffix("```").strip()

        start = stripped.find("{")
        end = stripped.rfind("}")
        if start == -1 or end == -1 or end < start:
            raise

        return schema.model_validate(json.loads(stripped[start : end + 1]))
