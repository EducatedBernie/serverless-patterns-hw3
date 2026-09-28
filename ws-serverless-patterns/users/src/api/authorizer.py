import json
import os
import urllib.request

from jose import jwt


USER_POOL_ID = os.environ['USER_POOL_ID']
CLIENT_ID = os.environ['APPLICATION_CLIENT_ID']
ADMIN_GROUP = os.environ['ADMIN_GROUP_NAME']
_keys = None


def lambda_handler(event, context):
    token = event['authorizationToken'].removeprefix('Bearer ').strip()
    arn = event['methodArn']
    region = arn.split(':')[3]
    issuer = f'https://cognito-idp.{region}.amazonaws.com/{USER_POOL_ID}'
    global _keys
    if _keys is None:
        with urllib.request.urlopen(f'{issuer}/.well-known/jwks.json', timeout=5) as response:
            _keys = json.load(response)
    try:
        claims = jwt.decode(token, _keys, algorithms=['RS256'], audience=CLIENT_ID, issuer=issuer)
        if claims.get('token_use') != 'id' or not claims.get('sub'):
            raise ValueError('Expected a Cognito ID token')
    except Exception as exc:
        raise Exception('Unauthorized') from exc

    principal = claims['sub']
    prefix = arn.rsplit(':', 1)[0] + ':' + '/'.join(arn.rsplit(':', 1)[1].split('/')[:2])
    if ADMIN_GROUP in claims.get('cognito:groups', []):
        resources = [f'{prefix}/*/users', f'{prefix}/*/users/*']
    else:
        resources = [f'{prefix}/{method}/users/{principal}' for method in ('GET', 'PUT', 'DELETE')]
    return {
        'principalId': principal,
        'policyDocument': {
            'Version': '2012-10-17',
            'Statement': [{'Action': 'execute-api:Invoke', 'Effect': 'Allow', 'Resource': resources}],
        },
    }
