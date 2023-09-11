import copy

from django.conf import settings
from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.contrib.admin.views.main import ChangeList
from django.db import models
from django.forms import ModelForm

from .compat import ct_admin
from .widgets import ElegantSplitDateTimeWidget
from .widgets import NumberInput


class SortableModelAdminBase:
    """
    Base class for SortableTabularInline and SortableModelAdmin
    """
    sortable = 'order'

    class Media:
        js = ('elegant/js/sortables.js',)


class SortableListForm(ModelForm):
    """
    Just Meta holder class
    """

    class Meta:
        widgets = {
            'order': NumberInput(attrs={'class': 'hide input-mini elegant-sortable'})
        }


class SortableChangeList(ChangeList):
    """
    Class that forces ordering by sortable param only
    """

    def get_ordering(self, request, queryset):
        return [self.model_admin.sortable, '-' + self.model._meta.pk.name]  # noqa


class SortableTabularInlineBase(SortableModelAdminBase):
    """
    Sortable tabular inline
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.ordering = (self.sortable,)
        self.fields = self.fields or []  # noqa

        if self.fields and self.sortable not in self.fields:
            self.fields = list(self.fields) + [self.sortable]

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == self.sortable:
            kwargs['widget'] = SortableListForm.Meta.widgets['order']

        return super().formfield_for_dbfield(db_field, **kwargs)  # noqa


class SortableTabularInline(SortableTabularInlineBase, admin.TabularInline):
    pass


class SortableGenericTabularInline(SortableTabularInlineBase, ct_admin.GenericTabularInline):
    pass


class SortableStackedInlineBase(SortableModelAdminBase):
    """
    Sortable stacked inline
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ordering = (self.sortable,)

    def get_fieldsets(self, *args, **kwargs):
        """
        Iterate all fieldsets and make sure sortable is in the first fieldset
        Remove sortable from every other fieldset, if by some reason someone
        has added it
        """
        fieldsets = super().get_fieldsets(*args, **kwargs)  # noqa
        sortable_added = False

        for fieldset in fieldsets:
            for line in fieldset:
                if not line or not isinstance(line, dict):
                    continue

                fields = line.get('fields')

                # Some use tuples for fields however they are immutable
                if isinstance(fields, tuple):
                    raise AssertionError(
                        'The fields attribute of your Inline is a tuple. '
                        'This must be list as we may need to modify it and '
                        'tuples are immutable.')

                if self.sortable in fields:
                    fields.remove(self.sortable)  # noqa

                # Add sortable field always as first
                if not sortable_added:
                    fields.insert(0, self.sortable)  # noqa
                    sortable_added = True
                    break

        return fieldsets

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == self.sortable:
            kwargs['widget'] = copy.deepcopy(SortableListForm.Meta.widgets['order'])
            kwargs['widget'].attrs['class'] += ' elegant-sortable-stacked'
            kwargs['widget'].attrs['rowclass'] = ' elegant-sortable-stacked-row'

        return super().formfield_for_dbfield(db_field, **kwargs)  # noqa


class SortableStackedInline(SortableStackedInlineBase, admin.StackedInline):
    pass


class SortableGenericStackedInline(SortableStackedInlineBase, ct_admin.GenericStackedInline):
    pass


class SortableModelAdmin(SortableModelAdminBase, ModelAdmin):
    """
    Sortable tabular inline
    """
    list_per_page = 500

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.ordering = (self.sortable,)

        if self.list_display and self.sortable not in self.list_display:
            self.list_display = list(self.list_display) + [self.sortable]

        self.list_editable = self.list_editable or []

        if self.sortable not in self.list_editable:
            self.list_editable = list(self.list_editable) + [self.sortable]

        self.exclude = self.exclude or []

        if self.sortable not in self.exclude:
            self.exclude = list(self.exclude) + [self.sortable]

    def merge_form_meta(self, form):
        """
        Prepare Meta class with order field widget
        """
        if not getattr(form, 'Meta', None):
            form.Meta = SortableListForm.Meta

        if not getattr(form.Meta, 'widgets', None):
            form.Meta.widgets = {}

        form.Meta.widgets[self.sortable] = SortableListForm.Meta.widgets['order']

    def get_changelist_form(self, request, **kwargs):
        form = super().get_changelist_form(request, **kwargs)
        self.merge_form_meta(form)

        return form

    def get_changelist(self, request, **kwargs):
        return SortableChangeList

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            max_order = obj.__class__.objects.aggregate(models.Max(self.sortable))

            try:
                next_order = max_order['%s__max' % self.sortable] + 1
            except TypeError:
                next_order = 1

            setattr(obj, self.sortable, next_order)

        super().save_model(request, obj, form, change)


# Quite aggressive detection and intrusion into Django CMS
# Didn't found any other solutions though
if 'cms' in settings.INSTALLED_APPS:
    try:
        from cms.admin.forms import PageForm  # noqa

        PageForm.Meta.widgets = {
            'publication_date': ElegantSplitDateTimeWidget,
            'publication_end_date': ElegantSplitDateTimeWidget,
        }
    except ImportError:
        pass


class SortableAdmin(admin.ModelAdmin):
    class Media:
        js = (
            'elegant/js/jquery-ui-1.10.3.sortable.min.js',
            'elegant/js/sortable.changelist.js',
        )


class SortableTabularInline(admin.TabularInline):
    class Media:
        js = (
            'elegant/js/jquery-ui-1.10.3.sortable.min.js',
            'elegant/js/sortable.tabular.inline.js',
        )


class SortableStackedInline(admin.StackedInline):
    class Media:
        js = (
            'elegant/js/jquery-ui-1.10.3.sortable.min.js',
            'elegant/js/sortable.stacked.inline.js',
        )
