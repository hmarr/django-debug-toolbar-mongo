# following PEP 386, versiontools will pick it up
__version__ = (0, 1, 7, "final", 0)

import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'debug_toolbar_mongo'

TEMPLATE_DIRS = (os.path.join(os.path.dirname(__file__), 'templates').replace('\\','/'), )
INSTALLED_APPS = ('debug_toolbar_mongo', )
