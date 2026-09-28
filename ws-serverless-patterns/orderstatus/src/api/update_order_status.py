import os

import boto3


table = boto3.resource('dynamodb').Table(os.environ['TABLENAME'])


def lambda_handler(event, context):
    detail = event['detail']
    status = detail.get('Status') or detail['status']
    table.update_item(
        Key={'userId': detail['userId'], 'orderId': detail['orderId']},
        UpdateExpression='SET #data.#status = :status',
        ConditionExpression='attribute_exists(userId) AND attribute_exists(orderId)',
        ExpressionAttributeNames={'#data': 'data', '#status': 'status'},
        ExpressionAttributeValues={':status': status},
    )
    return {'orderId': detail['orderId'], 'status': status}
