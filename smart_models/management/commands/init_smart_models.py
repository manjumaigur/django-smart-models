import json
import os
from pathlib import Path

from django.core.management.base import BaseCommand

from smart_models.fields import APIProviders
from smart_models.models import AIAPI

BASE_DIR = Path(__file__).resolve().parent.parent.parent
API_CONFIGS_DIR = os.path.join(BASE_DIR, "api_configurations")


class Command(BaseCommand):
    help = "Initialize smart models & fields"
    requires_migrations_checks = True
    requires_system_checks = []

    def handle(self, *args, **options):
        configs = None
        with open(os.path.join(API_CONFIGS_DIR, "configs.json"), "r") as f:
            configs = json.loads(f.read())

        for api_provider, api_name in APIProviders.choices:
            if api_provider in configs and configs[api_provider] != {}:
                api_configs = None
                with open(
                    os.path.join(API_CONFIGS_DIR, configs[api_provider]["configs"]), "r"
                ) as f:
                    api_configs = json.loads(f.read())

                for key, val in api_configs.items():
                    new_aiapi = AIAPI.objects.create(
                        name=f"{key}-{api_name}",
                        provider=api_provider,
                        configurations=val,
                    )

        self.stdout.write(
            "Initialized smart models. Open admin dashboard to see AI API configurations"
        )
