# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import json
import os
import boto3
import uuid
import pytest
from moto import mock_dynamodb
from contextlib import contextmanager
from unittest.mock import patch


ORDERS_MOCK_TABLE_NAME = 'Orders'


MOCK_ORDER = {
    "orderId": "2",
    "userId": "5c2db7f0-a714-4ca1-84ad-430cac333ab6",
    "totalAmount": "150",
    "Status": "PU",
    "timestamp": "2023-04-05T21:11:21.300436",
    "OrderTime": "10",
    "restaurantId": "dunkin98",
    "OrderItems": ["Chicken Sharma", "Fries"],
}

MOCK_ORDER_UPDATED = {
    "orderId": "2",
    "userId": "5c2db7f0-a714-4ca1-84ad-430cac333ab6",
    "totalAmount": "150",
    "Status": "DELIVERED",
    "timestamp": "2023-04-05T21:45:21.300436",
    "OrderTime": "10",
    "restaurantId": "dunkin99",
    "OrderItems": ["Chicken Sharma", "Fries"],
}


@contextmanager
def test_environment():

    with mock_dynamodb():
        set_up_dynamodb()
        put_data_dynamodb()
        yield


def set_up_dynamodb():
    conn = boto3.client('dynamodb')
    conn.create_table(
        TableName=ORDERS_MOCK_TABLE_NAME,
        KeySchema=[
            {'AttributeName': 'userId', 'KeyType': 'HASH'},
            {"AttributeName": 'orderId', 'KeyType': 'RANGE'},
        ],
        AttributeDefinitions=[
            {'AttributeName': 'userId', 'AttributeType': 'S'},
            {"AttributeName": 'orderId', 'AttributeType': 'S'},
        ],
        ProvisionedThroughput={'ReadCapacityUnits': 1, 'WriteCapacityUnits': 1},
    )


def put_data_dynamodb():
    conn = boto3.client('dynamodb')

    conn.put_item(
        TableName=ORDERS_MOCK_TABLE_NAME,
        Item={
            'orderId': {'S': MOCK_ORDER['orderId']},
            'userId': {'S': MOCK_ORDER['userId']},
            'totalAmount': {'S': MOCK_ORDER["totalAmount"]},
            'Status': {'S': MOCK_ORDER['Status']},
            'timestamp': {"S": MOCK_ORDER["timestamp"]},
            "OrderTime": {"S": MOCK_ORDER["OrderTime"]},
            "restaurantId": {"S": MOCK_ORDER["restaurantId"]},
            "OrderItems": {
                "L": [
                    {"S": MOCK_ORDER["OrderItems"][0]},
                    {"S": MOCK_ORDER["OrderItems"][1]},
                ]
            },
        },
    )


@patch.dict(
    os.environ,
    {'TABLENAME': ORDERS_MOCK_TABLE_NAME, 'AWS_XRAY_CONTEXT_MISSING': 'LOG_ERROR'},
)
def test_handler_success():

    with test_environment():
        from src.api import update_order_status

        with open('./events/event-update-order.json', 'r') as f:
            update_event = json.load(f)

        expected_response = {
            'orderId': MOCK_ORDER_UPDATED['orderId'],
            'userId': MOCK_ORDER_UPDATED['userId'],
            'totalAmount': MOCK_ORDER_UPDATED["totalAmount"],
            'Status': MOCK_ORDER_UPDATED['Status'],
            'timestamp': MOCK_ORDER_UPDATED["timestamp"],
            "OrderTime": MOCK_ORDER_UPDATED["OrderTime"],
            "restaurantId": MOCK_ORDER_UPDATED["restaurantId"],
            "OrderItems": MOCK_ORDER_UPDATED['OrderItems'],
        }

        ret = update_order_status.lambda_handler(update_event, '')
        assert ret['statusCode'] == 200
        data = json.loads(ret['body'])

        assert data == expected_response


def test_handler_exception():
    # mocked by excluding orderId from the event

    with test_environment():
        from src.api import update_order_status

        with open('./events/event-update-invalid-order.json', 'r') as f:
            update_event = json.load(f)

        ret = update_order_status.lambda_handler(update_event, '')
        assert ret['statusCode'] == 400
