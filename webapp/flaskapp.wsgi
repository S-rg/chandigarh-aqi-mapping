import sys
import logging
import traceback
from dotenv import load_dotenv

logging.basicConfig(stream=sys.stderr)

sys.path.insert(0, '/home/studentiotlab/aqi-dashboard/webapp')
os.chdir('/home/studentiotlab/aqi-dashboard/webapp')
load_dotenv('/home/studentiotlab/aqi-dashboard/.env')

from app import app as application
