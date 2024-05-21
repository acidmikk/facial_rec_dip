from __future__ import absolute_import, unicode_literals

# Это гарантирует, что Celery импортируется при запуске Django
from djangoProject.celery import app as celery_app

__all__ = ('celery_app',)