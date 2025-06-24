from urllib.parse import urljoin

from src.services.config.base import settings

CHECK_ACCESS_ALLOW_URL = urljoin(settings.API_AUTH_URL_BASE, settings.CHECK_ACCESS_URL)
CHECK_USERINFO_URL = urljoin(settings.API_AUTH_URL_BASE, settings.CHECK_USERINFO_URL)
