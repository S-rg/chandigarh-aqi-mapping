import sys
import logging
import traceback

logging.basicConfig(stream=sys.stderr)

sys.path.insert(0, '/var/www/flaskapp')
load_dotenv('/var/www/flaskapp/.env')


from app import app as application
