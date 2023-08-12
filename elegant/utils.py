import logging
from functools import wraps

from django import VERSION
from django.db.models.query import QuerySet
from django.urls import reverse

from .constants import CACHE_KEY_PREFIX
from .constants import DEBUG

try:
    from django.contrib.admin.sites import all_sites
except ImportError:
    from django.contrib import admin

    all_sites = [admin.site]

logger = logging.getLogger(__name__)


def django_major_version():
    return VERSION[:2]


def value_by_version(args):
    """
    Return value by version
    Return latest value if version not found
    :param args:
    :return:
    """

    version_map = args_to_dict(args)
    major_version = '.'.join(str(v) for v in django_major_version())
    return version_map.get(major_version, list(version_map.values())[-1])


def args_to_dict(args):
    """
    Convert template tag args to dict
    Format {% elegant_bc 1.5 'x' 1.6 'y' %} to { '1.5': 'x', '1.6': 'y' }
    :param args:
    :return:
    """

    return dict(zip(args[0::2], args[1::2]))


def snake_to_title_case(string: str) -> str:
    return ' '.join(string.split('_')).title()


def get_admin_change_url(obj: object) -> str:
    return reverse(f'admin:{obj._meta.app_label}_{obj._meta.model_name}_change', args=[obj.pk])  # noqa


def format_cache_key(model: str, field: str) -> str:
    return f'{CACHE_KEY_PREFIX}__{model}__{field}'


def log(message: str):  # pragma: no cover
    DEBUG and logger.debug(message)


def inspect(obj: object):  # pragma: no cover
    DEBUG and logger.debug(f'{str(obj): type(obj) - dir(obj)}')


class QuerySetIsh(QuerySet):
    """Takes an instance and mimics it coming from a QuerySet"""

    def __init__(self, instance=None, *args, **kwargs):
        try:
            model = instance._meta.model  # noqa
        except AttributeError:
            # Django 1.5 does this instead, getting the model may be overkill
            # we may be able to throw away all this logic
            model = instance._meta.concrete_model  # noqa

        self._doa_instance = instance
        super().__init__(model, *args, **kwargs)
        self._result_cache = [instance]

    def _clone(self, *args, **kwargs):
        # don't clone me, bro
        return self

    def get(self, *args, **kwargs):
        # Starting in Django 1.7, `QuerySet.get` started slicing to `MAX_GET_RESULTS`,
        # so to avoid messing with `__getslice__`, override `.get`.
        return self._doa_instance


def takes_instance_or_queryset(func):
    """Decorator that makes standard actions compatible"""

    @wraps(func)
    def decorated_function(self, request, queryset):
        # Function follows the prototype documented at:
        # https://docs.djangoproject.com/en/dev/ref/contrib/admin/actions/#writing-action-functions # noqa
        if not isinstance(queryset, QuerySet):
            queryset = QuerySetIsh(queryset)

        return func(self, request, queryset)

    return decorated_function


def get_django_model_admin(model):
    """Search Django ModelAdmin for passed model.

    Returns instance if found, otherwise None.
    """
    for admin_site in all_sites:
        registry = admin_site._registry  # noqa

        if model in registry:
            return registry[model]

    return None
