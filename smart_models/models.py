import os
import tempfile
import uuid
from typing import Union

from django.conf import settings
from django.core.files import File, storage, uploadedfile
from django.core.files.base import ContentFile
from django.db import models
from django.utils.translation import gettext_lazy as _

from .apis import (emojify_text, generate_thumbnail, generate_title,
                   spell_correct_text, summarize_text, transcribe_audio,
                   translate_audio, translate_text)
from .fields import (APIProviders, AudioToTextField, SmartImageField,
                     SmartTextField)


class AIAPI(models.Model):
    name = models.CharField(
        _("name"), max_length=50, blank=False, null=False, editable=False
    )
    provider = models.CharField(
        _("api provider"),
        max_length=6,
        choices=APIProviders.choices,
        default=APIProviders.OPENAI,
    )
    configurations = models.JSONField(_("configurations"), blank=False, null=False)

    def __str__(self) -> str:
        return self.name


class BaseAIModelMixin(models.Model):
    class Meta:
        abstract = True

    def _get_field(self, field_name: str) -> models.Field:
        return self._meta.get_field(field_name)


class TextAIModel(BaseAIModelMixin):
    class Meta:
        abstract = True

    def get_smart_text_field(self) -> Union[SmartTextField, None]:
        for field in self._meta.fields:
            if isinstance(field, SmartTextField):
                return field

        return None

    def save(self, *args, **kwargs) -> None:
        smart_text_field = self.get_smart_text_field()
        processed_text = None
        if smart_text_field is not None and len(smart_text_field.data_fields) != 0:
            for data_field in smart_text_field.data_fields:
                if not isinstance(data_field, str) and not (
                    isinstance(self._get_field(data_field), models.TextField)
                    or isinstance(self._get_field(data_field), models.CharField)
                ):
                    raise Exception(
                        "Only fields of type models.TextField and models.CharField can be passed to 'data_fields'"
                    )
                if processed_text is None:
                    processed_text = getattr(self, data_field)
                else:
                    # TODO: Validate if this is correct way to go forward and if not find a better solution
                    # for combining multiple data fields
                    processed_text += "\n" + getattr(self, data_field)
        elif smart_text_field is not None:
            # len(smart_text_field.data_fields) = 0
            processed_text = getattr(self, smart_text_field.attname)
        else:
            pass

        if processed_text is not None:
            api_provider = smart_text_field.api_provider
            if smart_text_field.spell_correct:
                processed_text = spell_correct_text(
                    processed_text, api_provider=api_provider
                )
            if smart_text_field.generate_title:
                processed_text = generate_title(
                    processed_text, max_title_length=smart_text_field.max_title_length
                )
            if smart_text_field.summarize:
                processed_text = summarize_text(
                    processed_text, api_provider=api_provider
                )
            if smart_text_field.translate:
                processed_text = translate_text(
                    processed_text,
                    target_language=smart_text_field.target_lang,
                    api_provider=api_provider,
                )
            if smart_text_field.emojify:
                processed_text = emojify_text(processed_text, api_provider=api_provider)
            self.__dict__[smart_text_field.attname] = processed_text
        return super().save(*args, **kwargs)


class ImageAIModel(BaseAIModelMixin):
    class Meta:
        abstract = True

    def get_smart_image_field(self) -> Union[SmartImageField, None]:
        for field in self._meta.fields:
            if isinstance(field, SmartImageField):
                return field

        return None

    def save(self, *args, **kwargs) -> None:
        smart_image_field = self.get_smart_image_field()
        processed_text = None
        if (
            smart_image_field is not None
            and len(smart_image_field.data_fields) != 0
            and smart_image_field.thumbnail
        ):
            for data_field in smart_image_field.data_fields:
                if not isinstance(data_field, str) and not (
                    isinstance(self._get_field(data_field), models.TextField)
                    or isinstance(self._get_field(data_field), models.CharField)
                ):
                    raise Exception(
                        "Only fields of type models.TextField and models.CharField can be passed to 'data_fields' when thumbnail=True"
                    )
                if processed_text is None:
                    processed_text = getattr(self, data_field)
                else:
                    # TODO: Validate if this is correct way to go forward and if not find a better solution
                    # for combining multiple data fields
                    processed_text += "\n" + getattr(self, data_field)
        else:
            pass

        if processed_text is not None:
            generated_image = None
            api_provider = smart_image_field.api_provider
            if smart_image_field.thumbnail:
                generated_image = generate_thumbnail(
                    processed_text,
                    smart_image_field.image_width,
                    smart_image_field.image_height,
                    api_provider=api_provider,
                )

            if generated_image is not None:
                self.__dict__[smart_image_field.attname].save(
                    f"{str(uuid.uuid4())}.{smart_image_field.image_extension}",
                    File(generated_image),
                    save=False,
                )
        return super().save(*args, **kwargs)


class AudioAIModel(BaseAIModelMixin):
    class Meta:
        abstract = True

    def get_audio_to_text_field(self) -> Union[AudioToTextField, None]:
        for field in self._meta.fields:
            if isinstance(field, AudioToTextField):
                return field

        return None

    def save(self, *args, **kwargs) -> None:
        smart_audio_text_field = self.get_audio_to_text_field()

        audio_paths = []
        delete_temp_idx = []
        if (
            smart_audio_text_field is not None
            and len(smart_audio_text_field.data_fields) != 0
            and (smart_audio_text_field)
        ):
            for i, data_field in enumerate(smart_audio_text_field.data_fields):
                if not isinstance(data_field, str) and not (
                    isinstance(self._get_field(data_field), models.FileField)
                ):
                    raise Exception(
                        "Only fields of type models.FileField can be passed to 'data_fields'"
                    )
                audio_field = getattr(self, data_field)
                # TODO: Better way to handle files
                if isinstance(audio_field.file, uploadedfile.InMemoryUploadedFile):
                    temp_path = os.path.join(
                        settings.MEDIA_ROOT,
                        str(uuid.uuid4()) + os.path.splitext(audio_field.file.name)[-1],
                    )
                    storage.default_storage.save(
                        temp_path, ContentFile(audio_field.file.read())
                    )
                    audio_paths.append(temp_path)
                    delete_temp_idx.append(i)
                elif isinstance(audio_field.file, uploadedfile.TemporaryUploadedFile):
                    audio_paths.append(audio_field.file.temporary_file_path())
        else:
            pass

        if len(audio_paths) != 0:
            generated_text = None
            api_provider = smart_audio_text_field.api_provider
            for i, audio_path in enumerate(audio_paths):
                _generated_text = None
                if smart_audio_text_field.transcribe:
                    _generated_text = transcribe_audio(
                        audio_path,
                        api_provider=api_provider,
                    )
                elif smart_audio_text_field.translate:
                    _generated_text = translate_audio(
                        audio_path, api_provider=api_provider
                    )

                if _generated_text is not None:
                    if len(audio_paths) == 1:
                        generated_text = _generated_text
                    else:
                        if generated_text is None:
                            generated_text = f"Audio {i+1}: " + _generated_text
                        else:
                            generated_text += f"\nAudio {i+1}: " + _generated_text

                if i in delete_temp_idx:
                    os.remove(audio_path)
            self.__dict__[smart_audio_text_field.attname] = generated_text
        return super().save(*args, **kwargs)
