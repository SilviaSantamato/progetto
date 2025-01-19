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
