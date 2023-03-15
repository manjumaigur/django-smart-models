import io
from typing import Any

import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation
from django.apps import apps
from django.conf import settings
from stability_sdk import client

from ..fields import APIProviders
from ._configs import get_task_configs


# TODO: Cache results
def _get_stability_ai_api(model: str) -> Any:
    return client.StabilityInference(
        key=settings.AI_API_SETTINGS["stability_ai"]["key"], verbose=True, engine=model
    )


def stabilityai_gen(
    configs: Any,
    task: str,
    text: str = None,
    image_width: int = 512,
    image_height: int = 512,
) -> Any:
    generated_image = None
    stability_api = _get_stability_ai_api(configs.configurations["model"])
    prompt = configs.configurations["tasks"][task].replace("article_placeholder", text)

    response = stability_api.generate(
        prompt=prompt,
        seed=992446758,  # using seed from documentation
        steps=configs.configurations["steps"],
        cfg_scale=configs.configurations["cfg_scale"],
        width=image_width,
        height=image_height,
        samples=1,
        guidance_preset=generation.GUIDANCE_PRESET_FAST_GREEN,
    )

    for resp in response:
        for artifact in resp.artifacts:
            if artifact.finish_reason == generation.FILTER:
                # TODO: retry generation
                pass
            if artifact.type == generation.ARTIFACT_IMAGE:
                generated_image = io.BytesIO(artifact.binary)
    return generated_image


def generate_thumbnail(
    text: str,
    image_width: int = 512,
    image_height: int = 512,
    api_provider: APIProviders = APIProviders.STABILITYAI,
) -> str:
    configs = get_task_configs("thumbnail", "image", api_provider)
    thumbnail = None
    if api_provider == APIProviders.STABILITYAI and configs is not None:
        thumbnail = stabilityai_gen(
            configs,
            "thumbnail",
            text,
            image_width=image_width,
            image_height=image_height,
        )

    return thumbnail
