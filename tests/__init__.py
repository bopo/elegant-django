import django

try:
    # Django 1.9+
    django.setup()
except Exception:
    pass

from tests.templatetags.elegant_menu import ElegantMenuTestCase, \
    ElegantMenuAdminRootURLTestCase, ElegantMenuAdminI18NURLTestCase, \
    ElegantMenuAdminCustomURLTestCase
from tests.templatetags.elegant_tags import ElegantTagsTestCase
from tests.templatetags.elegant_list import ElegantListTestCase
from tests.templates.form_tabs import FormTabsTestCase
from tests.config import ConfigTestCase, ConfigWithModelsTestCase
from tests.widgets import WidgetsTestCase
from tests.utils import UtilsTestCase

try:
    # Django 1.7+
    from django.test.runner import DiscoverRunner as DjangoTestEleganteRunner
except ImportError:
    from django.test.simple import DjangoTestEleganteRunner


class NoDbTestRunner(DjangoTestEleganteRunner):
    """A test suite runner that does not set up and tear down a database."""

    def setup_databases(self):
        """Overrides DjangoTestEleganteRunner"""
        pass

    def teardown_databases(self, *args):
        """Overrides DjangoTestEleganteRunner"""
        pass


class ElegantTestRunner(DjangoTestEleganteRunner):
    pass
