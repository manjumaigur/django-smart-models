# Django smart models
Make your Django models & fields smarter with built-in support for OpenAI & Stability AI APIs

## Quick start
1. Install `django-smart-models`
```bash
pip install django-smart-models
```

2. Add "smart_models" to your INSTALLED_APPS setting like this:

    INSTALLED_APPS = [
        ...
        'smart_models',
    ]

3. Run migrations to create smart_models models
```bash
python manage.py migrate
```

4. Initialize API configurations
```bash
python manage.py init_smart_models
```

5. Get OpenAI and Stability AI API keys
6. Add API keys to environment variables `OPENAI_API_KEY` and `STABILITYAI_API_KEY`


## Usage
Refer [demo]() for sample usage example

#### Fields
- `SmartTextField`
  Supports auto spell correction, translation, generating summary, generating emojis along with title generation tasks.
  - Base class: `models.TextField`
  - Parameters:
    - `data_fields`: `list[str]`
    - `spell_correct`: `bool`
    - `translate`: `bool`
    - `target_lan`: `str`
    - `generate_title`: `bool`
    - `max_title_length`: `int`
    - `summarize`: `bool`
    - `emojify`: `bool`
    - `api_provider`: `models.APIProviders`
- `SmartImageField`
  Supports thumbnail generation for a given article/text
  - Base class: `models.ImageField`
  - Parameters:
    - `data_fields`: `list[str]`
    - `thumbnail`: `bool`
    - `image_height`: `int`
    - `image_width`: `int`
    - `image_extension`: `str`
    - `api_provider`: `models.APIProviders`
- `AudioToTextField`
  Supports tasks of transcribing an audio or generating translation of an audio (text)
  - Base class: `models.TextField`
  - Parameters:
    - `data_fields`: `list[str]`
    - `transcribe`: `bool`
    - `translate`: `bool`
    - `api_provider`: `models.APIProviders`

#### Models
- `TextAIModel`
- `ImageAIModel`
- `AudioAIModel`



## TODO:
There is room for lots of improvements and will be taken up in future.
- [] async and celery based task execution
- [] Exception handling for OpenAI max_tokens
- [] Integrate all OpenAI APIs
- [] Stability AI API integration
- [] Hugging Face AI API integration
- [] GCP, Azure, AWS AI API integration


As this is more of a hobby project, updates would be pushed at very slow speed. But pull requests are welcome!