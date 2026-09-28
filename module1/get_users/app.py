import json

import boto3


table = boto3.resource('dynamodb').Table('serverless_workshop_intro')


def lambda_handler(event, context):
    return {'statusCode': 200, 'body': json.dumps(table.scan()['Items'])}
