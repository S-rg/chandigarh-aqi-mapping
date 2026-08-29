import os
import sys
import logging
from dotenv import load_dotenv

logging.basicConfig(stream=sys.stderr)

# Determine directories dynamically so the app can run from any path
WEBAPP_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(WEBAPP_DIR)

# Ensure the webapp directory is on sys.path and use it as CWD
if WEBAPP_DIR not in sys.path:
    sys.path.insert(0, WEBAPP_DIR)

os.chdir(WEBAPP_DIR)

# Load environment variables from the project root if the .env exists
dotenv_path = os.path.join(PROJECT_ROOT, '.env')
if os.path.isfile(dotenv_path):
    load_dotenv(dotenv_path)

from app import app as application
