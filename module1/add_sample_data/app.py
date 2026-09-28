import uuid

import boto3


def lambda_handler(event, context):
    table = boto3.resource('dynamodb').Table('serverless_workshop_intro')
    people = [
        {'userid': 'marivera', 'name': 'Martha Rivera'},
        {'userid': 'nikkwolf', 'name': 'Nikki Wolf'},
        {'userid': 'pasantos', 'name': 'Paulo Santos'},
    ]
    with table.batch_writer() as writer:
        for person in people:
            writer.put_item(Item={
                '_id': uuid.uuid4().hex,
                'Userid': person['userid'],
                'FullName': person['name'],
            })
    return {'message': f'Success. Added {len(people)} people to {table.name}.'}
