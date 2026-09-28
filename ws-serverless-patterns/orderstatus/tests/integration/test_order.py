# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import json
import requests
import boto3
import datetime
import time


def test_order_status_not_authenticated(global_config):
    response = get_order_status(
        global_config["Module5ApiEndpoint"], None, global_config['order']['orderId']
    )
    assert response.status_code == 401


def test_order_status(global_config):

    response = get_order_status(
        global_config["Module5ApiEndpoint"],
        global_config["regularUserIdToken"],
        global_config['order']['orderId'],
    )

    assert response.status_code == 200

    # test the response is the item we queried
    assert json.loads(response.content) == global_config['order']


# simulate an order update
def test_order_update_process(global_config):

    order = global_config['order']
    order['status'] = 'DELIVERED'

    eb_client = boto3.client('events')
    response = eb_client.put_events(
        Entries=[
            {
                'Time': datetime.datetime.now(),
                'Source': 'serverless-workshop-module5',
                'DetailType': 'Order Update Notification',
                'EventBusName': global_config['EventBusName'],
                'Detail': json.dumps(order),
            }
        ]
    )

    assert response['FailedEntryCount'] == 0

    time.sleep(
        3
    )  # Simulate an SLA for receiving a response, allowing updates to asynchronously take place

    # make another call to apigw to get teh status to see if the event now matches.
    response = get_order_status(
        global_config["Module5ApiEndpoint"],
        global_config["regularUserIdToken"],
        order['orderId'],
    )

    assert json.loads(response.content) == order


# helper function to execute order status api
def get_order_status(endpoint, token, orderId):

    response = requests.get(
        endpoint + f'orders/{orderId}', headers={"Authorization": token}
    )
    return response
