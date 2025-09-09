import sys
import logging
import traceback

logging.basicConfig(stream=sys.stderr)

sys.path.insert(0, '/var/www/flaskapp')

from app import app as application
