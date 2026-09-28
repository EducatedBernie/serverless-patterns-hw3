import json
import os
import uuid
from datetime import datetime, timezone

import boto3


table = boto3.resource('dynamodb').Table(os.environ['USERS_TABLE'])


def lambda_handler(event, context):
    route = f"{event['httpMethod']} {event['resource']}"
    userid = (event.get('pathParameters') or {}).get('userid')
    try:
        if route == 'GET /users':
            body = table.scan()['Items']
        elif route == 'GET /users/{userid}':
            body = table.get_item(Key={'userid': userid}).get('Item', {})
        elif route == 'DELETE /users/{userid}':
            table.delete_item(Key={'userid': userid})
            body = {}
        elif route in ('POST /users', 'PUT /users/{userid}'):
            body = json.loads(event.get('body') or '{}')
            if not isinstance(body, dict):
                return response(400, {'error': 'Expected a JSON object'})
            body['userid'] = userid if userid else body.get('userid') or str(uuid.uuid4())
            body['timestamp'] = datetime.now(timezone.utc).isoformat()
            table.put_item(Item=body)
        else:
            return response(400, {'error': 'Unsupported route'})
        return response(200, body)
    except (ValueError, TypeError):
        return response(400, {'error': 'Invalid JSON body'})


def response(status, body):
    return {'statusCode': status, 'headers': {'Content-Type': 'application/json'}, 'body': json.dumps(body)}
