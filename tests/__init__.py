import django
try:
    # Django 1.9+
    django.setup()
except Exception:
    pass

from tests.templatetags.suit_menu import SuitMenuTestCase, \
    SuitMenuAdminRootURLTestCase, SuitMenuAdminI18NURLTestCase, \
    SuitMenuAdminCustomURLTestCase
from tests.templatetags.suit_tags import SuitTagsTestCase
from tests.templatetags.suit_list import SuitListTestCase
from tests.templates.form_tabs import FormTabsTestCase
from tests.config import ConfigTestCase, ConfigWithModelsTestCase
from tests.widgets import WidgetsTestCase
from tests.utils import UtilsTestCase

try:
    # Django 1.7+
    from django.test.runner import DiscoverRunner as DjangoTestSuiteRunner
except ImportError:
    from django.test.simple import DjangoTestSuiteRunner


class NoDbTestRunner(DjangoTestSuiteRunner):
    """A test suite runner that does not set up and tear down a database."""

    def setup_databases(self):
        """Overrides DjangoTestSuiteRunner"""
        pass

    def teardown_databases(self, *args):
        """Overrides DjangoTestSuiteRunner"""
        pass


class ElegantTestRunner(DjangoTestSuiteRunner):
    pass
