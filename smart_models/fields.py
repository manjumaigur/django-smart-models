from django.db import models
from django.utils.translation import gettext_lazy as _


def _validate_smart_task_arguments(**kwargs) -> None:
    if kwargs["type"] is "text":
        if kwargs["translate"] and kwargs["target_lang"] is None:
            raise Exception(
                "value for 'target_lang' has to specified when translate=True"
            )
        if kwargs["generate_title"] and kwargs["max_title_length"] <= 2:
            raise Exception(
                "'max_title_length' should be atleast when generate_title=True"
            )
        if kwargs["generate_title"] and kwargs["summarize"]:
            raise Exception(
                "Only one of 'generate_title' or 'summarize' can be set to True"
            )

    if kwargs["type"] is "audio":
        if kwargs["translate"] and kwargs["transcribe"]:
            raise Exception(
                "Only one of 'translate' or 'transcribe' can be set to True"
            )


class APIProviders(models.TextChoices):
    OPENAI = "OPAI", _("OpenAI")
    STABILITYAI = "STBAI", _("Stability AI")
    GCP = "GCP", _("Google Cloud")
    AZURE = "AZC", _("Azure Cloud")
    AWS = "AWS", _("Amazon Web Services")


class SmartTextField(models.TextField):
    description = "smart models.TextField"

    def __init__(
        self,
        data_fields: list[str],
        spell_correct: bool = False,
        translate: bool = False,
        target_lang: str = None,
        generate_title: bool = False,
        max_title_length: int = 100,  # char length
        summarize: bool = False,
        emojify: bool = False,
        api_provider: APIProviders = APIProviders.OPENAI,
        *args,
        **kwargs,
    ):
        """
        to: str, is only used when translate = True
        Order of execution: correct_spelling -> summarize -> translate -> emojify
        """

        # TODO: Support for multiple tasks in one field
        _validate_smart_task_arguments(
            type="text",
            spell_correct=spell_correct,
            translate=translate,
            target_lang=target_lang,
            summarize=summarize,
            generate_title=generate_title,
            max_title_length=max_title_length,
            emojify=emojify,
        )
        self.spell_correct = spell_correct
        self.translate = translate
        self.target_lang = target_lang
        self.summarize = summarize
        self.emojify = emojify
        self.generate_title = generate_title
        self.max_title_length = max_title_length
        self.data_fields = data_fields
        self.api_provider = api_provider
        super().__init__(*args, **kwargs)
        self.help_text = f"spell_correct={spell_correct}; translate={translate}; target_lang={target_lang}; \
            summarize={summarize}; emojify={emojify}; generate_title={generate_title}; max_title_length={max_title_length}; api={api_provider}"

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        # Only include in kwargs if it's not the default
        if not self.spell_correct:
            kwargs["spell_correct"] = self.spell_correct
        if not self.translate and self.target_lang is not None:
            kwargs["translate"] = self.translate
            kwargs["target_lang"] = self.target_lang
        if not self.summarize:
            kwargs["summarize"] = self.summarize
        if not self.emojify:
            kwargs["emojify"] = self.emojify
        if not self.generate_title:
            kwargs["generate_title"] = self.generate_title
            kwargs["max_title_length"] = self.max_title_length
        kwargs["data_fields"] = self.data_fields
        kwargs["api_provider"] = self.api_provider
        return name, path, args, kwargs


class SmartImageField(models.ImageField):
    description = "smart models.ImageField"

    def __init__(
        self,
        data_fields: list[str],
        thumbnail: bool = True,
        image_height: int = 512,
        image_width: int = 512,
        image_extension: str = "png",
        api_provider: APIProviders = APIProviders.STABILITYAI,
        *args,
        **kwargs,
    ):
        # TODO: Argument validation
        # TODO: Support for multiple tasks in one field
        _validate_smart_task_arguments(
            type="image",
            thumbnail=thumbnail,
            image_height=image_height,
            image_width=image_width,
            image_extension=image_extension,
        )
        self.data_fields = data_fields
        self.thumbnail = thumbnail
        self.image_width = image_width
        self.image_height = image_height
        self.image_extension = image_extension
        self.api_provider = api_provider
        super().__init__(*args, **kwargs)
        self.help_text = f"thumbnail={thumbnail};api={api_provider}"

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        # Only include in kwargs if it's not the default
        if not self.thumbnail:
            kwargs["thumbnail"] = self.thumbnail
        kwargs["image_width"] = self.image_width
        kwargs["image_height"] = self.image_height
        kwargs["image_extension"] = self.image_extension
        kwargs["data_fields"] = self.data_fields
        kwargs["api_provider"] = self.api_provider
        return name, path, args, kwargs


class AudioToTextField(models.TextField):
    def __init__(
        self,
        data_fields: list[str],
        transcribe: bool = False,
        translate: bool = False,
        api_provider: APIProviders = APIProviders.OPENAI,
        *args,
        **kwargs,
    ):
        # TODO: Argument validation
        # TODO: Support for multiple tasks in one field
        _validate_smart_task_arguments(
            type="audio",
            transcribe=transcribe,
            translate=translate,
        )
        self.transcribe = transcribe
        self.translate = translate
        self.data_fields = data_fields
        self.api_provider = api_provider
        super().__init__(*args, **kwargs)
        self.help_text = f"api={api_provider}"

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        # Only include in kwargs if it's not the default
        if not self.transcribe:
            kwargs["transcribe"] = self.transcribe
        if not self.translate:
            kwargs["translate"] = self.translate
        kwargs["data_fields"] = self.data_fields
        kwargs["api_provider"] = self.api_provider
        return name, path, args, kwargs
