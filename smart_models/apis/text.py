from typing import Any

import openai
from django.apps import apps
from django.conf import settings

from ..fields import APIProviders
from ._configs import get_task_configs

openai.api_key = settings.AI_API_SETTINGS["openai"]["key"]


def _parse_openai_chat_prompts(
    task_configs: dict,
    original_language: str,
    target_language: str = None,
    task: str = "translate",
    role: str = "system",
) -> str:
    parsed_prompt = None
    if task != "translate":
        parsed_prompt = task_configs[role].replace(
            "default_language", original_language.capitalize()
        )

    elif task == "translate" and target_language != None:
        parsed_prompt = (
            task_configs[role]
            .replace("language_1", original_language.capitalize())
            .replace("language_2", target_language.capitalize())
        )

    if role == "system":
        return parsed_prompt + task_configs["result_format_rules"]

    return parsed_prompt


def _postprocess_result(result: str, default_result_key: str) -> str:
    if "Text:" and "Result:" in result:
        result = result[result.find("Result:") + 7 :].strip()
        if default_result_key.lower() in result.lower():
            # TODO: More detailed inspection of return statement/fine tuning prompt
            result = None

    return result


def openai_chat(model: str, messages: list[dict], default_result_key: str = "") -> str:
    response = openai.ChatCompletion.create(model=model, messages=messages)
    return _postprocess_result(
        response.choices[0].message.content.split("\n")[-1].strip(), default_result_key
    )


def resolve_openai_text_calls(
    configs: Any,
    original_text: str,
    task: str,
    target_language: str = None,
    max_title_length: int = 3,
) -> str:
    # TODO: Identify original language automatically
    original_language = "english"
    user_message = _parse_openai_chat_prompts(
        configs.configurations["tasks"][task],
        original_language=original_language,
        target_language=target_language,
        task=task,
        role="user",
    )
    user_message = user_message.replace("original_text", original_text)
    if task == "generate_title":
        user_message = user_message.replace("max_title_length", str(max_title_length))
    system_message = _parse_openai_chat_prompts(
        configs.configurations["tasks"][task],
        original_language=original_language,
        target_language=target_language,
        task=task,
        role="system",
    )
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_message},
    ]

    result_text = openai_chat(
        configs.configurations["model"],
        messages,
        configs.configurations["tasks"][task]["default_result_key"],
    )
    if result_text is None:
        result_text = original_text

    return result_text


def translate_text(
    original_text: str,
    target_language: str,
    api_provider: APIProviders = APIProviders.OPENAI,
) -> str:
    configs = get_task_configs("translate", "text", api_provider)
    translated_text = None
    if api_provider == APIProviders.OPENAI and configs is not None:
        translated_text = resolve_openai_text_calls(
            configs, original_text, "translate", target_language=target_language
        )

    return translated_text


def summarize_text(
    original_text: str, api_provider: APIProviders = APIProviders.OPENAI
) -> str:
    configs = get_task_configs("summarize", "text", api_provider)
    summarized_text = None
    if api_provider == APIProviders.OPENAI and configs is not None:
        summarized_text = resolve_openai_text_calls(
            configs, original_text, task="summarize"
        )
    return summarized_text


def spell_correct_text(
    original_text: str, api_provider: APIProviders = APIProviders.OPENAI
) -> str:
    configs = get_task_configs("spell_correct", "text", api_provider)
    corrected_text = None
    if api_provider == APIProviders.OPENAI and configs is not None:
        corrected_text = resolve_openai_text_calls(
            configs, original_text, task="spell_correct"
        )
    return corrected_text


def emojify_text(
    original_text: str, api_provider: APIProviders = APIProviders.OPENAI
) -> str:
    configs = get_task_configs("emojify", "text", api_provider)
    corrected_text = None
    if api_provider == APIProviders.OPENAI and configs is not None:
        corrected_text = resolve_openai_text_calls(
            configs, original_text, task="emojify"
        )
    return corrected_text


def generate_title(
    original_text: str,
    max_title_length: int,
    api_provider: APIProviders = APIProviders.OPENAI,
) -> str:
    if max_title_length <= 2:
        raise Exception("max_title_length should be greater than or equal to three")
    configs = get_task_configs("generate_title", "text", api_provider)
    generated_title = None
    if api_provider == APIProviders.OPENAI and configs is not None:
        generated_title = resolve_openai_text_calls(
            configs,
            original_text,
            task="generate_title",
            max_title_length=max_title_length,
        )
    return generated_title
