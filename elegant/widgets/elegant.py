from django import forms
from django.contrib.admin.widgets import AdminDateWidget
from django.contrib.admin.widgets import AdminTimeWidget
from django.forms import Select
from django.forms import Textarea
from django.forms import TextInput
from django.templatetags.static import static
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

from .. import utils

django_version = utils.django_major_version()


class NumberInput(TextInput):
    """
    HTML5 Number input
    Left for backwards compatibility
    """

    input_type = 'number'


class HTML5Input(TextInput):
    """
    Supports any HTML5 input
    http://www.w3schools.com/html/html5_form_input_types.asp # noqa
    """

    def __init__(self, attrs=None, input_type=None):
        self.input_type = input_type
        super().__init__(attrs)


#
class LinkedSelect(Select):
    """
    Linked select - Adds link to foreign item, when used with foreign key field
    """

    def __init__(self, attrs=None, choices=()):
        attrs = _make_attrs(attrs, classes='linked-select')
        super().__init__(attrs, choices)


class EnclosedInput(TextInput):
    """
    Widget for bootstrap appended/prepended inputs
    """

    def __init__(self, attrs=None, prepend=None, append=None):
        """
        For prepend, append parameters use string like %, $ or html
        """
        self.prepend = prepend
        self.append = append

        super().__init__(attrs=attrs)

    def enclose_value(self, value):  # noqa
        """
        If value doesn't starts with html open sign "<", enclose in add-on tag
        """
        if value.startswith('<'):
            return value

        if value.startswith('icon-'):
            value = f'<i class="{value}"></i>'

        return f'<span class="add-on">{value}</span>'

    def render(self, name, value, attrs=None, renderer=None):

        if django_version < (2, 0):
            output = super().render(name, value, attrs)
        else:
            output = super().render(name, value, attrs, renderer)

        div_classes = []

        if self.prepend:
            div_classes.append('input-prepend')
            self.prepend = self.enclose_value(self.prepend)
            output = ''.join((self.prepend, output))

        if self.append:
            div_classes.append('input-append')
            self.append = self.enclose_value(self.append)
            output = ''.join((output, self.append))

        return mark_safe('<div class="{}">{}</div>'.format(' '.join(div_classes), output))


class AutosizedTextarea(Textarea):  # noqa
    """
    Autosized Textarea - textarea height dynamically grows based on user input
    """

    def __init__(self, attrs=None):
        new_attrs = _make_attrs(attrs, {'rows': 2}, 'autosize')
        super().__init__(new_attrs)

    @property
    def media(self):
        return forms.Media(js=[static('elegant/js/jquery.autosize-min.js')])

    def render(self, name, value, attrs=None, renderer=None):
        if django_version < (2, 0):
            output = super().render(name, value, attrs)
        else:
            output = super().render(name, value, attrs, renderer)

        output += mark_safe(f"<script type=\"text/javascript\">Elegant.$('#id_{name}').autosize();</script>")

        return output


#
# Original date widgets with addition html
#
class ElegantDateWidget(AdminDateWidget):

    def __init__(self, attrs=None, format=None):  # noqaf
        defaults = {'placeholder': _('Date:')[:-1]}
        new_attrs = _make_attrs(attrs, defaults, 'vDateField input-small')
        super().__init__(attrs=new_attrs, format=format)

    if django_version < (4, 2):
        def render(self, name, value, attrs=None, renderer=None):
            if django_version < (2, 0):
                output = super().render(name, value, attrs)
            else:
                output = super().render(name, value, attrs, renderer)

            return mark_safe(
                f'<div class="input-append elegant-date">{output}<span class="add-on">'
                f'<i class="icon-calendar"></i></span></div>')


class ElegantTimeWidget(AdminTimeWidget):

    def __init__(self, attrs=None, format=None):  # noqa
        defaults = {'placeholder': _('Time:')[:-1]}
        new_attrs = _make_attrs(attrs, defaults, 'vTimeField input-small')
        super().__init__(attrs=new_attrs, format=format)

    if django_version < (4, 2):
        def render(self, name, value, attrs=None, renderer=None):
            if django_version < (2, 0):
                output = super().render(name, value, attrs)
            else:
                output = super().render(name, value, attrs, renderer)

            return mark_safe(f'<div class="input-append elegant-date elegant-time">{output}<span class="add-on">'
                             f'<i class="icon-time"></i></span></div>')


class ElegantSplitDateTimeWidget(forms.SplitDateTimeWidget):
    """
    A SplitDateTime Widget that has some admin-specific styling.
    """

    def __init__(self, attrs=None):
        widgets = [ElegantDateWidget, ElegantTimeWidget]
        forms.MultiWidget.__init__(self, widgets, attrs)

    # if django_version < (1, 11):
    #     def format_output(self, rendered_widgets):
    #         out_tpl = f'<div class="datetime">{rendered_widgets[0]} {rendered_widgets[1]}</div>'
    #         return mark_safe(out_tpl)

    if django_version < (4, 2):
        def render(self, name, value, attrs=None, renderer=None):
            output = super().render(name, value, attrs, renderer)
            return mark_safe('<div class="datetime">%s</div>' % output)


class ElegantProgressWidget(forms.Widget):
    """
    A SplitDateTime Widget that has some admin-specific styling.
    """


def _make_attrs(attrs, defaults=None, classes=None):
    result = defaults.copy() if defaults else {}

    if attrs:
        result.update(attrs)

    if classes:
        result['class'] = ' '.join((classes, result.get('class', '')))

    return result
