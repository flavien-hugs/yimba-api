from urllib.parse import urljoin

from src.services.config.base import settings

CHECK_ACCESS_ALLOW_URL = urljoin(settings.API_AUTH_URL_BASE, settings.API_AUTH_CHECK_ACCESS_ENDPOINT)
