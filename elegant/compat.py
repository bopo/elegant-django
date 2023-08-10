import django

try:
    from importlib import import_module
except ImportError:
    pass

try:
    from django.templatetags.future import url
except ImportError:
    from django.template.defaulttags import url

try:
    from django.contrib.contenttypes import admin as ct_admin
except ImportError:
    from django.contrib.contenttypes import generic as ct_admin  # Django < 1.8

if django.VERSION[:2] < (1, 8):
    from django.template import Context

    tpl_context_class = Context
else:
    tpl_context_class = dict
