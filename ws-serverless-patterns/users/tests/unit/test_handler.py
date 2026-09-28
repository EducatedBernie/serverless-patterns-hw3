import json
import os

os.environ.setdefault('USERS_TABLE', 'test-users')
os.environ.setdefault('AWS_DEFAULT_REGION', 'us-east-2')
os.environ.setdefault('AWS_ACCESS_KEY_ID', 'test')
os.environ.setdefault('AWS_SECRET_ACCESS_KEY', 'test')
os.environ.setdefault('USER_POOL_ID', 'us-east-2_test')
os.environ.setdefault('APPLICATION_CLIENT_ID', 'test-client')
os.environ.setdefault('ADMIN_GROUP_NAME', 'apiAdmins')

from src.api import authorizer, users


class FakeTable:
    def __init__(self):
        self.items = {}

    def scan(self):
        return {'Items': list(self.items.values())}

    def get_item(self, Key):
        item = self.items.get(Key['userid'])
        return {'Item': item} if item else {}

    def put_item(self, Item):
        self.items[Item['userid']] = Item

    def delete_item(self, Key):
        self.items.pop(Key['userid'], None)


def test_user_create_read_delete(monkeypatch):
    monkeypatch.setattr(users, 'table', FakeTable())
    created = users.lambda_handler({'httpMethod': 'POST', 'resource': '/users', 'body': '{"name":"Test"}'}, None)
    assert created['statusCode'] == 200
    userid = json.loads(created['body'])['userid']
    path = {'httpMethod': 'GET', 'resource': '/users/{userid}', 'pathParameters': {'userid': userid}}
    assert json.loads(users.lambda_handler(path, None)['body'])['name'] == 'Test'
    assert len(json.loads(users.lambda_handler({'httpMethod': 'GET', 'resource': '/users'}, None)['body'])) == 1
    path['httpMethod'] = 'DELETE'
    assert users.lambda_handler(path, None)['statusCode'] == 200
    path['httpMethod'] = 'GET'
    assert json.loads(users.lambda_handler(path, None)['body']) == {}


def test_authorizer_scopes_regular_user_and_admin(monkeypatch):
    monkeypatch.setattr(authorizer, '_keys', {'keys': []})
    claims = {'token_use': 'id', 'sub': 'test-user'}
    monkeypatch.setattr(authorizer.jwt, 'decode', lambda *args, **kwargs: claims)
    event = {'authorizationToken': 'test', 'methodArn': 'arn:aws:execute-api:us-east-2:123456789012:api/Prod/GET/users'}
    regular = authorizer.lambda_handler(event, None)['policyDocument']['Statement'][0]['Resource']
    assert regular == [f'arn:aws:execute-api:us-east-2:123456789012:api/Prod/{method}/users/test-user'
                       for method in ('GET', 'PUT', 'DELETE')]
    claims['cognito:groups'] = ['apiAdmins']
    admin = authorizer.lambda_handler(event, None)['policyDocument']['Statement'][0]['Resource']
    assert 'arn:aws:execute-api:us-east-2:123456789012:api/Prod/*/users' in admin
