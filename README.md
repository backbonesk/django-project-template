# Django project template

Simple quickstart for [Django](https://www.djangoproject.com/)-based projects created as
[cookiecutter](https://github.com/cookiecutter/cookiecutter) template.

## What's inside?

- Exception handling (`ProblemDetailException`, `ValidationException`
  prepared for [django_api_forms](https://github.com/Sibyx/django_api_forms))
- Basic security (signature middleware, Argon password hasher)
- Hard/soft delete for models
- Custom `User` model
- Response objects (`SingleResponse`, `ValidationResponse`)
- [pydantic](https://github.com/pydantic/pydantic) response serialisation
- Custom JSON encoder
- Configuration using `.env` files
- [Sentry](https://sentry.io/welcome) integration
- Dependency management using [poetry](https://python-poetry.org/)
- Multi-environment settings
- E-mail testing using [django-imap-backend](https://github.com/Sibyx/django-imap-backend) in `development` environment
- CRON job management

### Bundled dependencies

- [django_api_forms](https://github.com/Sibyx/django_api_forms): Request validation
- [python-dotenv](https://github.com/theskumar/python-dotenv): `.env` handling
- [porcupine-python](https://github.com/zurek11/porcupine-python): Response serialisation
- [django-imap-backend](https://github.com/Sibyx/django-imap-backend): Custom e-mail backend for simplified testing
- [django-celery-beat](https://github.com/celery/django-celery-beat): CRON jobs

## Usage

You need to have installed [cookiecutter](https://github.com/cookiecutter/cookiecutter) in your system, then you can
call. You will be asked a few questions about the new project (name, target directory):

```shell
cookiecutter gh:backbonesk/django-project-template
```

## Next steps

1. Check `pyproject.toml` and change the `authors` list
2. `cd {{ directory_name }}`
3. `python -m venv venv`
4. `poetry install && poetry update`
5. Remove stuff you don't need (template is feature rich on purpose, it's easier to delete than create)
6. Call `python manage.py makemigrations` and then `python manage.py migrate`
7. You are supposed to create superuser using `python manage.py createsuperuser`
8. When the project is set up, you can call `{baseurl}/status` to check if everything is up and running
9. Take a coffee and celebrate life, you saved a plenty of time!
---
Made with ❤️ and ☕️ BACKBONE s.r.o. (c) 2025
