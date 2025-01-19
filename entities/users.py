import boto3
import json
import os
from flask import jsonify
from entities.converter import convert_to_dynamo, convert_from_dynamo

dynamodb_client = boto3.client('dynamodb')

if os.environ.get('IS_OFFLINE'):
    dynamodb_client = boto3.client(
        'dynamodb', region_name='localhost', endpoint_url='http://localhost:8000'
    )

USERS_TABLE = os.environ['USERS_TABLE']

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