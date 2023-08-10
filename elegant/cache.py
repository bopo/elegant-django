from io import BytesIO

from django.core.cache import cache
from django.core.files.uploadedfile import InMemoryUploadedFile

from .constants import CACHE_TIMEOUT
from .utils import log


class FileCache:
    """Cache file data and retain the file upon confirmation."""
    timeout = CACHE_TIMEOUT

    def __init__(self):
        self.cache = cache
        self.cached_keys = []

    def set(self, key, upload):
        """
        Set file data to cache for 1000s

        :param key: cache key
        :param upload: file data
        """
        try:  # noqa: WPS229
            state = {
                'name': upload.name,
                'size': upload.size,

                'charset': upload.charset,
                'content': upload.file.read(),

                'content_type': upload.content_type,
            }

            upload.file.seek(0)
            self.cache.set(key, state, self.timeout)

            log(f'Setting file cache with {key}')
            self.cached_keys.append(key)
        except AttributeError:  # pragma: no cover
            pass  # noqa: WPS420

    def get(self, key):
        """
        Get the file data from cache using specific cache key

        :param key: cache key
        :return: File data
        """
        upload = None
        state = self.cache.get(key)

        if state:
            file = BytesIO()
            file.write(state['content'])

            upload = InMemoryUploadedFile(
                content_type=state['content_type'],
                charset=state['charset'],
                field_name='file',
                name=state['name'],
                size=state['size'],
                file=file,
            )

            upload.file.seek(0)
            log(f'Getting file cache with {key}')

        return upload

    def delete(self, key):
        """
        Delete file data from cache

        :param key: cache key
        """
        self.cache.delete(key)
        self.cached_keys.remove(key)

    def delete_all(self):
        """Delete all cached file data from cache."""
        self.cache.delete_many(self.cached_keys)
        self.cached_keys = []
