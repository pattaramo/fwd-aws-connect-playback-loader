#status

import json, uuid
from datetime import datetime
import pytz

optionsResponse = {
    'statusCode': 204,
    'statusDescription': 'no content',
    'headers': {
        'Content-Type': 'text/html',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': '*',
        'Access-Control-Allow-Methods': '*'
    },
    'isBase64Encoded': False
}


def setResponse(code, desc, body):
    result = {
        'statusCode': code,
        'statusDescription': desc,
        'headers': {
            'Content-Type': 'text/html',
            'Access-Control-Allow-Origin': '*'
        },
        'isBase64Encoded': False,
    }
    if body != None:
        result['body'] = json.dumps(body)
    return result



def convert_to_unix_timestamp(datetime_str):
    datetime_obj = datetime.datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
    unix_timestamp = int(datetime_obj.timestamp())
    return unix_timestamp






'''
def template_leadLoader(data, current_rows, request_rows, response_rows):
    now = datetime.now()
    return {
        "campaign_uuid": data['campaign_uuid'],
        "campaign_lead_count": current_rows,
        "start_time": now.strftime("%Y/%m/%d %H:%M:%S"),
        "end_time": None,
        "lead_loader_status": "running",
        "lead_loader_status_message": "Request data",
        "watermark_start": "",
        "watermark_end": "",
        "request_rows": request_rows,
        "response_rows": response_rows
    }


def template_leadLoader_update(data, leadCount, request_rows, sf_rows):
    now = datetime.now()
    return {
        "campaign_uuid": data['campaign_uuid'],
        "campaign_lead_count": leadCount,
        "start_time": data['start_time'],
        "end_time": now.strftime("%Y/%m/%d %H:%M:%S"),
        "lead_loader_status": 'success',
        "lead_loader_status_message": "update success",
        "watermark_start": "",
        "watermark_end": "",
        "request_rows": request_rows,
        "response_rows": sf_rows
    }


def template_sfdata(campaign_uuid, row, sf_object_name):
    if row[8] == None:
        row[8] = 0
    return {
        'campaign_uuid': campaign_uuid,
        'outbound_uuid': str(uuid.uuid4()),
        'account_id': None,
        'sf_record_id': row[1],
        'dnis_1': row[2],
        'dnis_2': row[3],
        'dnis_3': row[4],
        'attribute_1': row[5],
        'attribute_2': row[6],
        'attribute_3': row[7],
        'attempt': int(row[8]),
        'status': row[9],
        'contact_after': row[10],
        'object_name': sf_object_name,
    }'''
