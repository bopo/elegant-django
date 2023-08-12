from datetime import datetime
from datetime import time

from django import forms
from django.conf import settings
from django.contrib import admin
from django.utils import timezone
from django.utils.translation import pgettext

from .elegant import ElegantDateWidget


class DateRangeForm(forms.Form):

    def __init__(self, *args, **kwargs):
        """ Automatically generate form fields with dynamic names based on the filtering field name """

        self.field_name = kwargs.pop('field_name', 'date')
        self.title = kwargs.pop('title', 'Date').title()

        super().__init__(*args, **kwargs)

        self.fields[f'{self.field_name}_start'] = forms.DateField(
            widget=ElegantDateWidget(attrs={'placeholder': self.title, 'style': 'width=330px;'}),
            label=pgettext('date', '从'), required=False)

        self.fields[f'{self.field_name}_end'] = forms.DateField(
            widget=ElegantDateWidget(attrs={'placeholder': self.title}),
            label=pgettext('date', '至'), required=False)

    def start_date(self):
        if self.is_valid():
            start = self.cleaned_data.get(f'{self.field_name}_start')

            if start:
                start = datetime.combine(start, time.min)

                if settings.USE_TZ:
                    return timezone.make_aware(start)

            return start

    def end_date(self):
        if self.is_valid():
            end = self.cleaned_data.get(f'{self.field_name}_end')

            if end:
                end = datetime.combine(end, time.max)

                if settings.USE_TZ:
                    return timezone.make_aware(end)

            return end

    class Media:
        css = {'all': ('elegant/css/date_range_filter.css',), }


class DateRangeFilter(admin.FieldListFilter):
    template = 'elegant/date_range_filter.html'
    form = None

    def expected_parameters(self):
        return f'{self.field_path}_start', f'{self.field_path}_end'

    def choices(self, cl):
        return [{'query_string': [], }]

    def get_form(self, request):
        return DateRangeForm(data=request.GET, field_name=self.field_path, title=self.title)

    def queryset(self, request, queryset):
        """
        That's the trick - we create self.form when django tries to get our queryset.
        This allows to create unbount and bound form in the single place.
        """

        self.form = self.get_form(request)

        start_date = self.form.start_date()
        end_date = self.form.end_date()

        if self.form.is_valid() and (start_date or end_date):
            args = self._get_filter_args(start=start_date, end=end_date, )
            return queryset.filter(**args)

    def _get_filter_args(self, start, end):
        filter_args = {}

        if start:
            filter_args[f'{self.field_path}__gte'] = start

        if end:
            filter_args[f'{self.field_path}__lte'] = end

        return filter_args
