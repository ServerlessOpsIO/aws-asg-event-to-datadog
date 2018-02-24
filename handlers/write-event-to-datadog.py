'''Write an ASG scaling event to Datadog'''

import datadog
import logging
import json
import os

log_level = os.environ.get('LOG_LEVEL', 'info')
logging.root.setLevel(logging.getLevelName(log_level))
_logger = logging.getLogger(__name__)

DATADOG_API_KEY = os.environ.get('DATADOG_API_KEY')
DATADOG_APP_KEY = os.environ.get('DATADOG_APP_KEY')

def handler(event, context):
    '''Function entry.'''
    pass

