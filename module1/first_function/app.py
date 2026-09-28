import json


def lambda_handler(event, context):
    line_item = {'sku': 1234242, 'color': 'blue', 'quantity': 42, 'in_stock': True}
    return {'statusCode': 200, 'body': json.dumps(line_item, sort_keys=True)}
