import os
from typing import Any

import openai
from django.conf import settings

from ..fields import APIProviders
from ._configs import get_task_configs

openai.api_key = settings.AI_API_SETTINGS["openai"]["key"]


def transcribe_audio(
    audio_file: str, api_provider: APIProviders = APIProviders.OPENAI
) -> str:
    configs = get_task_configs("transcribe", "audio", api_provider)
    transcribed_text = None
    if api_provider == APIProviders.OPENAI and configs is not None:
        if os.path.splitext(audio_file)[-1] not in [
            ".mp3",
            ".mp4",
            ".mpeg",
            ".mpga",
            ".m4a",
            ".wav",
            ".webm",
        ]:
            raise Exception(
                f"audio format {os.path.splitext(audio_file)[-1]} is not supported by {api_provider}"
            )

        with open(audio_file, "rb") as f:
            transcript = openai.Audio.transcribe(configs.configurations["model"], f)
            if "text" in transcript:
                transcribed_text = transcript["text"]

    return transcribed_text


def translate_audio(
    audio_file: str, api_provider: APIProviders = APIProviders.OPENAI
) -> str:
    configs = get_task_configs("translate", "audio", api_provider)
    translated_text = None
    if api_provider == APIProviders.OPENAI and configs is not None:
        if os.path.splitext(audio_file)[-1] not in [
            ".mp3",
            ".mp4",
            ".mpeg",
            ".mpga",
            ".m4a",
            ".wav",
            ".webm",
        ]:
            raise Exception(
                f"audio format {os.path.splitext(audio_file)[-1]} is not supported by {api_provider}"
            )

        with open(audio_file, "rb") as f:
            translation = openai.Audio.translate(configs.configurations["model"], f)
            if "text" in translation:
                translated_text = translation["text"]

    return translated_text
