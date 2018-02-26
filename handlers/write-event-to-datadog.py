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

INFO_TYPES = [
    'EC2 Instance-launch Lifecycle Action',
    'EC2 Instance-terminate Lifecycle Action'
]

ERROR_TYPES = [
    'EC2 Instance Launch Successful',
    'EC2 Instance Terminate Successful'
]

SUCCESS_TYPES = [
    'EC2 Instance Launch Unsuccessful',
    'EC2 Instance Terminate Unsuccessful'

]

def _create_datadog_event(event: dict) -> dict:
    datadog_event = {}

    datadog_event['title'] = event.get('detail-type')
    datadog_event['date_happened'] = int(iso8601.parse_date(event.get('time')).timestamp())
    datadog_event['source_type_name'] = SOURCE_TYPE_NAME
    datadog_event['host'] = event.get('detail').get('EC2InstanceId')

    datadog_event['text'] = _get_event_text(
        asg=event.get('detail').get('AutoScalingGroupName'),
        host=event.get('detail').get('EC2InstanceId'),
        region=event.get('region')
        detail=datadog_event['title']
    )

    event_detail_type = event.get('detail-type')
    if event_detail_type in INFO_TYPES:
        datadog_event['alert_type'] = 'info'
    elif event_detail_type in SUCCESS_TYPES:
        datadog_event['alert_type'] = 'success'
    else:
        datadog_event['alert_type'] = 'error'

    return datadog_event


def _get_event_text(asg: str, host: str, region:str, detail: str) -> str:
    msg = '''
    ASG: {asg}
    Host: {host}
    Region: {region}

    Detail: {detail}
    '''
    return msg.format(asg=asg, host=host, region=region detail=detail)


def handler(event, context):
    '''Function entry.'''
    _logger.info('Event received: {}'.format(json.dumps(event)))

    datadog_event = _create_datadog_event(event)
    resp = datadog.api.Event.create(**datadog_event)

    _logger.info(json.dumps(resp))
    return json.dumps(resp)

