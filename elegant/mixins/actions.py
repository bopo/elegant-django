from django import forms
from django import VERSION
from django.contrib import messages
from django.http import Http404
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.urls import re_path as url
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic.detail import SingleObjectMixin

from ..components import Dropdown
from ..utils import get_django_model_admin


class AdminRowActionsMixin:
    """ModelAdmin mixin to add row actions just like adding admin actions"""

    # rowactions = []
    _named_row_actions = {}

    @property
    def media(self):
        css = super().media._css  # noqa
        css['all'] = css.get('all', [])
        css['all'].extend(['elegant/css/jquery.dropdown.min.css'])

        js = super().media._js  # noqa
        js.extend(['elegant/js/jquery.dropdown.min.js', ])

        media = forms.Media(css=css, js=js)
        return media

    def get_list_display(self, request):
        self._request = request  # noqa
        list_display = super().get_list_display(request)  # noqa

        if '_row_actions' not in list_display:
            list_display += ('_row_actions',)

        return list_display

    def get_actions_list(self, obj, include_pk=True):

        def to_dict(tool_name):
            return dict(name=tool_name, label=getattr(tool, 'label', tool_name).replace('_', ' ').title())

        items = []

        row_actions = self.get_row_actions(obj)
        url_prefix = '{}/'.format(obj.pk if include_pk else '')

        for tool in row_actions:

            if isinstance(tool, str):  # Just a str naming a callable
                tool_dict = to_dict(tool)

                items.append({
                    'label': tool_dict['label'],
                    'url': f'{url_prefix}rowactions/{tool}/',
                    'method': tool_dict.get('POST', 'GET')
                })

            elif isinstance(tool, dict):  # A parameter dict
                tool['enabled'] = tool.get('enabled', True)

                # If 'action' is specified then use our generic url in preference to 'url' value
                if 'action' in tool:
                    if isinstance(tool['action'], tuple):
                        self._named_row_actions[tool['action'][0]] = tool['action'][1]
                        tool['url'] = f'{url_prefix}rowactions/{tool["action"][0]}/'
                    else:
                        tool['url'] = f'{url_prefix}rowactions/{tool["action"]}/'

                items.append(tool)

        return items

    def _row_actions(self, obj):
        items = self.get_actions_list(obj)

        if items:
            html = Dropdown(label=_('Actions'), items=items, request=getattr(self, '_request')).render()
            return mark_safe(html)

        return ''

    _row_actions.short_description = ''

    if VERSION < (1, 9):
        _row_actions.allow_tags = True

    def get_tool_urls(self):
        """Gets the url patterns that route each tool to a special view"""
        my_urls = [
            url(r'^(?P<pk>[0-9a-f-]+)/rowactions/(?P<tool>\w+)/$',
                self.admin_site.admin_view(ModelToolsView.as_view(model=self.model)))  # noqa
        ]

        return my_urls

    ###################################
    # EXISTING ADMIN METHODS MODIFIED #
    ###################################

    def get_urls(self):
        """Prepends `get_urls` with our own patterns"""
        return self.get_tool_urls() + super().get_urls()  # noqa

    ##################
    # CUSTOM METHODS #
    ##################

    def get_row_actions(self, obj):
        return getattr(self, 'rowactions', False) or []  # noqa

    def get_change_actions(self, request, object_id, form_url):

        # If we're also using django_object_actions
        # then try to reuse row actions as object actions

        change_actions = super().get_change_actions(request, object_id, form_url)  # noqa

        # Make this reuse opt-in
        if getattr(self, 'reuse_row_actions_as_object_actions', False):

            obj = self.model.objects.get(pk=object_id)  # noqa
            row_actions = self.get_actions_list(obj, False) if obj else []

            for row_action in row_actions:
                # Object actions only supports strings as action indentifiers
                if isinstance(row_action, str):
                    change_actions.append(row_action)
                elif isinstance(row_action, dict):
                    if isinstance(row_action['action'], str):
                        change_actions.append(row_action['action'])
                    if isinstance(row_action['action'], tuple):
                        change_actions.append(str(row_action['action'][1]))

        return change_actions


class ModelToolsView(SingleObjectMixin, View):
    """A special view that run the tool's callable"""

    def get(self, request, **kwargs):
        # SingleObjectMixin's `get_object`. Works because the view
        # is instantiated with `model` and the urlpattern has `pk`.

        obj = self.get_object()
        model_admin = get_django_model_admin(obj.__class__)

        if not model_admin:
            raise Http404(f'Can not find ModelAdmin for {obj.__class__}')

        # Look up the action in the following order:
        # 1. in the named_row_actions dict (for lambdas etc)
        # 2. as a method on the model admin
        # 3. as a method on the model
        if kwargs['tool'] in model_admin._named_row_actions:  # noqa
            action_method = model_admin._named_row_actions[kwargs['tool']]  # noqa
            ret = action_method(request=request, queryset=obj)
        elif getattr(model_admin, kwargs['tool'], False):
            action_method = getattr(model_admin, kwargs['tool'])
            # TODO should the signature actually be (obj, request) for consistancy?
            ret = action_method(request=request, queryset=obj)
        elif getattr(obj, kwargs['tool'], False):
            action_method = getattr(obj, kwargs['tool'])
            ret = action_method()
        else:
            raise Http404

        # If the method returns a response use that,
        # otherwise redirect back to the url we were called from
        if isinstance(ret, HttpResponse):
            response = ret
        else:
            back = request.META['HTTP_REFERER']
            response = HttpResponseRedirect(back)

        return response

    # Also allow POST
    post = get

    def message_user(self, request, message):  # noqa
        # Copied from django.contrib.admin.options
        # Included to mimic admin actions
        messages.info(request, message)
