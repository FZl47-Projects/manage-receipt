import os

PRODUCTION = os.environ.get('PRODUCTION_STATE', False)

from .base import *

if PRODUCTION:
    from .production import *
else:
    from .dev import *
