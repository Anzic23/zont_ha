import asyncio
import logging

from ..const import ZONT_API_URLS

_LOGGER = logging.getLogger(__name__)


class ZontRequestManager:
    """Класс для управления запросами к актуальным endpoint api ZONT."""

    def __init__(self, session):
        self._session = session
        self._base_urls = ZONT_API_URLS
        self._last_base_url = ZONT_API_URLS[0]

    @staticmethod
    def _build_url(base_url: str, path: str) -> str:
        return f'{base_url}{path}'

    async def request(self, method: str, path: str, **kwargs):
        last_exc = None

        urls = self._base_urls.copy()

        if self._last_base_url != self._base_urls[0]:
            urls.remove(self._last_base_url)
            urls.insert(0, self._last_base_url)

        for base_url in urls:
            url = self._build_url(base_url, path)

            try:
                _LOGGER.debug(f'Request {method} {url}')

                resp = await self._session.request(method, url, **kwargs)

                if resp.status < 500:
                    if base_url != self._last_base_url:
                        _LOGGER.info(f'Switching API endpoint to {base_url}')

                    self._last_base_url = base_url
                    return resp

                _LOGGER.warning(f'Server error {resp.status} on {base_url}')

            except asyncio.TimeoutError:
                _LOGGER.warning(f'Timeout while connecting to {base_url}')
                last_exc = None

            except Exception as e:
                _LOGGER.warning(f'Request failed for {base_url}: {e}')
                last_exc = e

        raise last_exc or Exception('All API endpoints failed')