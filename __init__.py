from django.apps import apps
from django.conf import settings
from os.path import dirname, abspath, join, isdir


def load_tests(loader, tests, pattern):
    """
    This is called by pytest when running tests.
    Loads tests for installed apps only taking care if we are testing intranet or internet.
    """
    this_dir = dirname(abspath(__file__))
    for app_name in settings.INSTALLED_APPS:
        app_dir = join(this_dir, app_name)
        if apps.is_installed(app_name) and isdir(app_dir):
            app_tests = loader.discover(
                start_dir=app_dir,
                pattern=pattern
            )
            tests.addTests(app_tests)
    return tests