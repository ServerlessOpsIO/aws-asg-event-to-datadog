'''Write an ASG scaling event to Datadog'''

import datadog
import logging
import iso8601
import json
import os

log_level = os.environ.get('LOG_LEVEL', 'INFO')
logging.root.setLevel(logging.getLevelName(log_level))
_logger = logging.getLogger(__name__)

DATADOG_API_KEY = os.environ.get('DATADOG_API_KEY')
DATADOG_APP_KEY = os.environ.get('DATADOG_APP_KEY')
datadog.initialize(api_key=DATADOG_API_KEY, app_key=DATADOG_APP_KEY)

SOURCE_TYPE_NAME = 'AWS/ASG'

def _create_datadog_event(event: dict) -> dict:
    datadog_event = {}

    datadog_event['title'] = event.get('detail-type')
    datadog_event['date_happened'] = int(iso8601.parse_date(event.get('time')).timestamp())
    datadog_event['source_type_name'] = SOURCE_TYPE_NAME
    datadog_event['host'] = event.get('detail').get('EC2InstanceId')

    datadog_event['text'] = '{asg}[{host}]: {detail}'.format(
        asg=event.get('detail').get('AutoScalingGroupName'),
        host=event.get('detail').get('EC2InstanceId'),
        detail=datadog_event['title']
    )

    if _is_asg_launch_action(event):
        datadog_event['alert_type'] = 'info'

    elif _is_asg_launch_successful(event):
        datadog_event['alert_type'] = 'success'

    elif _is_asg_launch_unsuccessful(event):
        datadog_event['alert_type'] = 'error'

    elif _is_asg_terminate_action(event):
        datadog_event['alert_type'] = 'info'

    elif _is_asg_terminate_successful(event):
        datadog_event['alert_type'] = 'success'

    elif _is_asg_terminate_unsuccessful(event):
        datadog_event['alert_type'] = 'error'

    return datadog_event


def _is_asg_launch_action(event: dict) -> bool:
    '''Check if event is an ASG launch event.'''
    return event.get('detail-type') == 'EC2 Instance-launch Lifecycle Action'


def _is_asg_launch_successful(event: dict) -> dict:
    '''Check if event is a successful launch event'''
    return event.get('detail-type') == 'EC2 Instance Launch Successful'


def _is_asg_launch_unsuccessful(event: dict) -> dict:
    '''Check if event is a successful launch event'''
    return event.get('detail-type') == 'EC2 Instance Launch Unsuccessful'


def _is_asg_terminate_action(event: dict) -> dict:
    '''Check if event is a successful launch event'''
    return event.get('detail-type') == 'EC2 Instance-terminate Lifecycle Action'


def _is_asg_terminate_successful(event: dict) -> dict:
    '''Check if event is a successful terminate event'''
    return event.get('detail-type') == 'EC2 Instance Terminate Successful'


def _is_asg_terminate_unsuccessful(event: dict) -> dict:
    '''Check if event is a successful terminate event'''
    return event.get('detail-type') == 'EC2 Instance Terminate Unsuccessful'


def handler(event, context):
    '''Function entry.'''
    _logger.info('Event received: {}'.format(json.dumps(event)))

    datadog_event = _create_datadog_event(event)
    resp = datadog.api.Event.create(**datadog_event)

    _logger.info(json.dumps(resp))
    return json.dumps(resp)

