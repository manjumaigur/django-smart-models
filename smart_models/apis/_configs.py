from typing import Any

from django.apps import apps
from django.db.models import Q

from ..fields import APIProviders


def get_task_configs(
    task: str, model_type: str, api_provider: APIProviders = APIProviders.OPENAI
) -> Any:
    # TODO: Add exceptions and better way to handle circular imports
    aiapi = apps.get_model("smart_models.AIAPI")
    configs = None

    # TODO: If no instance is created, read from json file
    configs = aiapi.objects.get(
        Q(configurations__tasks__has_key=task) & Q(configurations__type=model_type),
        provider=api_provider,
    )

    return configs
