import datetime

import pytest
from django.conf import settings
from django.contrib import admin
from django.contrib.admin.helpers import AdminReadonlyField
from django.db import models
from django.test import TestCase

# from django.utils.encoding import python_2_unicode_compatible
from elegant import utils
from elegant.templatetags.elegant_tags import elegant_conf, elegant_date, elegant_time, \
    admin_url, field_contents_foreign_linked, elegant_bc, elegant_bc_value

django_version = utils.django_major_version()


# @python_2_unicode_compatible
class Country(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name


# @python_2_unicode_compatible
class City(models.Model):
    name = models.CharField(max_length=64)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class CityAdmin(admin.ModelAdmin):
    readonly_fields = ('country',)


admin.site.register(Country)
admin.site.register(City, CityAdmin)


class ElegantTagsTestCase(TestCase):
    """
    TemplateTags - elegant_tags.py test case
    """

    def test_elegant_config_string(self):
        admin_name = 'Custom Name'
        settings.SUIT_CONFIG = {
            'ADMIN_NAME': admin_name
        }
        value = elegant_conf('ADMIN_NAME')
        self.assertEqual(value, admin_name)
        self.assertTrue('Safe' in value.__class__.__name__)

    def test_elegant_config_mark_safe(self):
        list = (1, 2, 3)
        settings.SUIT_CONFIG = {
            'SOME_LIST': list
        }
        value = elegant_conf('SOME_LIST')
        self.assertEqual(value, list)
        self.assertEqual(value.__class__.__name__, 'tuple')

    def test_elegant_date_and_time(self):
        settings.SUIT_CONFIG = {
            'HEADER_DATE_FORMAT': 'Y-m-d',
            'HEADER_TIME_FORMAT': 'H:i',
        }
        self.assertEqual(datetime.datetime.now().strftime('%Y-%m-%d'),
                         elegant_date({}, {}).render({}))
        self.assertEqual(datetime.datetime.now().strftime('%H:%M'),
                         elegant_time({}, {}).render({}))

    def test_admin_url(self):
        country = Country(pk=1, name='USA')
        assert '/country/1' in admin_url(country)

    @pytest.mark.skipif(django_version > (3, 1), reason='not supported django v3.1+')
    def test_field_contents_foreign_linked(self):
        country = Country(pk=1, name='France')
        city = City(pk=1, name='Paris', country=country)

        ma = CityAdmin(City, admin.site)

        # Create form
        request = None
        form = ma.get_form(request, city)
        form.instance = city
        form.fields = '__all__'

        ro_field = AdminReadonlyField(form, 'country', True, ma)
        self.assertEqual(country.name, field_contents_foreign_linked(ro_field))

        # Now it should return as link
        ro_field.model_admin.linked_readonly_fields = ('country',)
        assert admin_url(country) in field_contents_foreign_linked(ro_field)

    def test_elegant_bc(self):
        args = [utils.django_major_version(), 'a']
        self.assertEqual(utils.value_by_version(args), elegant_bc(*args))

    def test_elegant_bc_value(self):
        args = [utils.django_major_version(), 'a']
        self.assertEqual(utils.value_by_version(args), elegant_bc_value(*args))
