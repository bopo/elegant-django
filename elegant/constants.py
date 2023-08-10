import weakref

from django.conf import settings
from django.template.loader import render_to_string

SAVE = '_save'

SAVE_AS_NEW = '_saveasnew'
ADD_ANOTHER = '_addanother'

SAVE_AND_CONTINUE = '_continue'
SAVE_ACTIONS = [SAVE, SAVE_AS_NEW, ADD_ANOTHER, SAVE_AND_CONTINUE]

CONFIRM_ADD = '_confirm_add'
CONFIRM_CHANGE = '_confirm_change'
CONFIRMATION_RECEIVED = '_confirmation_received'

CACHE_TIMEOUT = getattr(settings, 'ADMIN_CONFIRM_CACHE_TIMEOUT', 1000)

CACHE_KEYS = {
    'object': 'admin_confirm__confirmation_object',
    'post': 'admin_confirm__confirmation_request_post',
}

CACHE_KEY_PREFIX = getattr(settings, 'ADMIN_CONFIRM_CACHE_KEY_PREFIX', 'admin_confirm__file_cache')

DEBUG = getattr(settings, 'ADMIN_CONFIRM_DEBUG', False)


class BaseComponent:
    template = None
    instances = []

    def __init__(self, **kwargs):
        self.__class__.instances.append(weakref.proxy(self))
        self.request = kwargs.pop('request')

        self.context = kwargs
        self.context['dom_id'] = self.get_unique_id()

    @classmethod
    def get_unique_id(cls):
        return f'{cls.__name__.lower()}-{len(cls.instances)}'

    def render(self):
        return render_to_string(self.template, self.context, request=self.request)

    def __unicode__(self):
        return self.render()


class Dropdown(BaseComponent):
    template = 'actions/dropdown.html'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
