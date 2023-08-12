from django.contrib import admin
from django.utils.translation import gettext
from tests.mixins import ModelsTestCaseMixin, UserTestCaseMixin
from tests.models import Book, BookAdmin, test_app_label

try:
    from django.core.urlresolvers import reverse
except ImportError:
    # For Django >= 2.0
    from django.urls import reverse


app_label = test_app_label()


class TabbedBookAdmin(BookAdmin):
    list_filter = ('id', 'name',)
    elegant_form_tabs = (('tab1', 'Tab1'), ('tab2', gettext('Tab2')))
    elegant_form_includes = None


admin.site.unregister(Book)
admin.site.register(Book, TabbedBookAdmin)


class FormTabsTestCase(ModelsTestCaseMixin, UserTestCaseMixin):
    def setUp(self):
        self.login_superuser()
        self.url = reverse('admin:%s_book_add' % app_label)
        self.get_response(self.url)

    def test_tabs_appearance(self):
        for x in range(0, 2):
            vars = (TabbedBookAdmin.elegant_form_tabs[x][0],
                    TabbedBookAdmin.elegant_form_tabs[x][1])
            self.assertContains(self.response, '<li><a href="#%s">%s</a></li>' %
                                               vars)

    def test_template_includes(self):
        elegant_form_include = 'admin/date_hierarchy.html'
        TabbedBookAdmin.elegant_form_includes = ((elegant_form_include, 'top', 'tab1'),)
        self.get_response(self.url)
        self.assertTemplateUsed(self.response,
                                'elegant/includes/change_form_includes.html')
        self.assertTemplateUsed(self.response, elegant_form_include)
        self.assertContains(self.response,
                            '<div class="elegant-include elegant-tab elegant-tab-tab1">')
