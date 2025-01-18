import boto3
import json
import os
from flask import jsonify

dynamodb_client = boto3.client('dynamodb')

if os.environ.get('IS_OFFLINE'):
    dynamodb_client = boto3.client(
        'dynamodb', region_name='localhost', endpoint_url='http://localhost:8000'
    )

USERS_TABLE = os.environ['USERS_TABLE']

def convert_to_dynamo(value):
    
    # Converte i valori python nel formato DynamoDB
    
    if isinstance(value, dict):
        return {'M': {k: convert_to_dynamo(v) for k, v in value.items()}}
    elif isinstance(value, list):
        return {'L': [convert_to_dynamo(v) for v in value]}
    elif isinstance(value, str):
        return {'S': value}
    elif isinstance(value, bool):
        return {'BOOL': value}
    elif isinstance(value, (int, float)):
        return {'N': str(value)}
    elif value is None:
        return {'NULL': True}
    else:
        raise ValueError(f"Unsupported data type: {type(value)}")

def convert_from_dynamo(value):
    
    # Converte i valori DynamoDB in formato python
    
    if 'M' in value:
        return {k: convert_from_dynamo(v) for k, v in value['M'].items()}
    elif 'L' in value:
        return [convert_from_dynamo(v) for v in value['L']]
    elif 'S' in value:
        return value['S']
    elif 'N' in value:
        return float(value['N']) if '.' in value['N'] else int(value['N'])
    elif 'BOOL' in value:
        return value['BOOL']
    elif 'NULL' in value:
        return None
    else:
        raise ValueError(f"Unsupported DynamoDB value: {value}")


def create(body):
    user_id = body.get('userId')
    name = body.get('name')
    data = body.get('data') or {}
    
    if not user_id or not name:
        return jsonify({'error': 'Please provide both "userId" and "name"'}), 400
    if not isinstance(data, dict):
        return jsonify({'error': '"data" must be a valid map/dictionary'}), 400
    
    # Converte la mappa data per dynamo
    
    dynamo_data = convert_to_dynamo(data)

    item = {
        'userId': {'S': user_id},
        'name': {'S': name},
        'data': dynamo_data
    }
    print("Dati convertiti per DynamoDB:", item)

    dynamodb_client.put_item(
        TableName=USERS_TABLE, Item=item
    )

    return jsonify({'userId': user_id, 'name': name, 'data': data})


def get(user_id):
    result = dynamodb_client.get_item(
        TableName=USERS_TABLE, Key={'userId': {'S': user_id}}
    )
    item = result.get('Item')
    if not item:
        return jsonify({'error': 'Could not find user with provided "userId"'}), 404

    # Formatta il campo data a json
    data = item.get('data')
    formatted_data = convert_from_dynamo(data) if data else {}

    return jsonify(
        {'userId': item.get('userId').get('S'), 
         'name': item.get('name').get('S'), 
         'data': formatted_data}
    )