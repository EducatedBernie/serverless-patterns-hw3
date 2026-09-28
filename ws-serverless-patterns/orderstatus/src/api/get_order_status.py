import json
import os

import boto3


table = boto3.resource('dynamodb').Table(os.environ['TABLENAME'])


def lambda_handler(event, context):
    order_id = event['pathParameters']['orderid']
    user_id = event['requestContext']['authorizer']['claims']['sub']
    item = table.get_item(Key={'userId': user_id, 'orderId': order_id}).get('Item')
    if item is None:
        return {'statusCode': 404, 'body': json.dumps({'error': 'Order not found'})}
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({'orderId': order_id, 'status': item['data']['status']}),
    }
