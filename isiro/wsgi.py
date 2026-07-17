"""WSGI config for isiro project."""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "isiro.settings")
application = get_wsgi_application()
