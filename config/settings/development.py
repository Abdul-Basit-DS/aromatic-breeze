"""Development settings."""
from .base import *

DEBUG = True
ALLOWED_HOSTS = ['*']


INTERNAL_IPS = ['127.0.0.1']

# Use console email backend in development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Simple cache for development
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Disable axes in development
AXES_ENABLED = False
