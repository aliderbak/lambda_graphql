
import botocore
import boto3
from boto3.dynamodb.conditions import Key, Attr
import os


def run(event, contex):
    dynamodb = boto3.resource('dynamodb', region_name='eu-central-1')
    level = event['level'] # 1 for all data, 2 get by asset, 3 get by type
    # getting user_id by decode cognito token
    user_id = event['cognitoPoolClaims']['user_id']
    start = event['start']
    end = event['end']
    table = dynamodb.Table(os.getenv('TABLE_NAME'))
    response = []
    err = None
    if level == 2:
        asset = event['asset']
        response, err = get_data_by_asset_between_two_dates(table, user_id, asset,start, end,index_name='gsi_index')
    elif level == 3:
        type = event['type']
        response,err = get_data_by_type_between_two_dates(table,user_id,type,start,end,index_name='lsi_index')
        
    else:
        response, err = get_data_between_two_dates(table, user_id, start, end)
    if err == None:
        return {"data": response,"error":0}
    else:
        return {"data": 0,"error":1}


def get_data_between_two_dates(table, pk, start, end):
    try:
        response = table.query(
            KeyConditionExpression=Key('pk').eq(
                pk) & Key('sk').between(start, end)
        )
        data = []
        data = response['Items']
        while 'LastEvaluatedKey' in response:

            lastkey = response['LastEvaluatedKey']
            response = table.query(
                KeyConditionExpression=Key('pk').eq(
                    pk) & Key('sk').between(start, end),
                ExclusiveStartKey=response['LastEvaluatedKey']
            )
            data = data + response['Items']
        return data, None
    except botocore.exceptions.ClientError as error:
        return None, f'{error}'

    except botocore.exceptions.ParamValidationError as error:
        return None, f'{error}'


def get_data_by_asset_between_two_dates(table, pk, asset, start, end, index_name):
    try:
        response = table.query(
            KeyConditionExpression=Key('pk').eq(
                pk) & Key('asset').eq(asset),
            FilterExpression=Attr('sk').between(start, end),
            IndexName=index_name,
            ScanIndexForward=False
        )
        data = []
        data = response['Items']
        while 'LastEvaluatedKey' in response:

            lastkey = response['LastEvaluatedKey']
            response = table.query(
                KeyConditionExpression=Key('pk').eq(
                    pk) & Key('asset').eq(asset),
                FilterExpression=Attr('sk').between(start, end),
                IndexName=index_name,
                ScanIndexForward=False,
                ExclusiveStartKey=response['LastEvaluatedKey']
            )
            data = data + response['Items']
        return data, None
    except botocore.exceptions.ClientError as error:
        return None, f'{error}'

    except botocore.exceptions.ParamValidationError as error:
        return None, f'{error}'




def get_data_by_type_between_two_dates(table, pk, type, start, end, index_name):
    try:
        response = table.query(
            KeyConditionExpression=Key('pk').eq(
                pk) & Key('type').eq(type),
            FilterExpression=Attr('sk').between(start, end),
            IndexName=index_name,
            ScanIndexForward=False
        )
        data = []
        data = response['Items']
        while 'LastEvaluatedKey' in response:

            lastkey = response['LastEvaluatedKey']
            response = table.query(
                KeyConditionExpression=Key('pk').eq(
                    pk) & Key('type').eq(type),
                FilterExpression=Attr('sk').between(start, end),
                IndexName=index_name,
                ScanIndexForward=False,
                ExclusiveStartKey=response['LastEvaluatedKey']
            )
            data = data + response['Items']
        return data, None
    except botocore.exceptions.ClientError as error:
        return None, f'{error}'

    except botocore.exceptions.ParamValidationError as error:
        return None, f'{error}'
