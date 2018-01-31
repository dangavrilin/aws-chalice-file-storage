import boto3
import uuid
from chalice import BadRequestError, Chalice, Response
from boto3.dynamodb.conditions import Key, Attr

db = boto3.resource('dynamodb')
s3 = boto3.client('s3')

app = Chalice(app_name='aws-chalice-file-storage')
app.debug = True

bucket = app.app_name
table = db.Table(app.app_name)


def get_item(user_id, collection_id, position=None):
    if position:
        response = table.query(
            KeyConditionExpression=Key('userId').eq(user_id),
            FilterExpression=Attr('collectionId').eq(collection_id) & Attr('position').eq(int(position))
        )
    else:
        response = table.query(
            KeyConditionExpression=Key('userId').eq(user_id),
            FilterExpression=Attr('collectionId').eq(collection_id)
        )
    return response['Items']


def last_position(user_id, collection_id):
    items = get_item(user_id, collection_id)
    position_list = []
    for item in items:
        position_list.append(item.get('position'))
    if len(position_list) == 0:
        return 0
    return max(position_list)


def reorganize_items(user_id, collection_id):
    items = get_item(user_id, collection_id)

    # reorder position
    def fill_empty_number(_dct):
        k, v = sorted(_dct, key=_dct.get), sorted(_dct.values())
        result = {}
        for n in range(len(_dct)):
            if v[n] != n + 1:
                result[k[n]] = n + 1
        return result

    dct = {}
    for item in items:
        dct[item['fileId']] = item['position']

    for k, v in fill_empty_number(dct).items():
        table.update_item(
            Key={
                'userId': user_id,
                'fileId': k
            },
            UpdateExpression="set #position = :p",
            ExpressionAttributeNames={'#position': 'position'},
            ExpressionAttributeValues={':p': int(v)}
        )
    return get_item(user_id, collection_id)


def check_params():
    params = app.current_request.query_params
    if not params:
        raise BadRequestError('Wrong parameters')
    return params


@app.route('/v1/images', methods=['GET'])
def get_file():
    params = check_params()
    items = get_item(params['userId'], params['collectionId'])

    if not items:
        raise BadRequestError('Wrong parameters')

    sorted_items = sorted(items, key=lambda k: k['position'])

    for item in sorted_items:
        item['href'] = 'https://s3.ap-south-1.amazonaws.com/exme/{}'.format(item['fileName'])

    return Response(body={'collection:': sorted_items},
                    status_code=200,
                    headers={'Content-Type': 'application/json'})


@app.route('/v1/images', methods=['POST'], content_types=['application/octet-stream'])
def upload_file():
    params = check_params()
    if set(params.keys()) != {'userId', 'collectionId'}:
        raise BadRequestError('Wrong parameters')

    # get raw body of POST request
    body = app.current_request.raw_body

    # write body to tmp file
    file_id = str(uuid.uuid4())
    file_name = file_id + '.jpg'
    tmp_file_name = '/tmp/' + file_name
    with open(tmp_file_name, 'wb') as tmp_file:
        tmp_file.write(body)

    # upload tmp file to s3 bucket
    try:
        s3.upload_file(tmp_file_name, bucket, file_name)
    except Exception:
        raise BadRequestError("Can't upload file")

    next_position = last_position(params['userId'], params['collectionId']) + 1

    table.put_item(Item={
        'userId': params['userId'],
        'fileId': file_id,
        'collectionId': params['collectionId'],
        'fileName': file_name,
        'position': next_position
    })

    return Response(body={'message': 'Upload successful'},
                    status_code=200,
                    headers={'Content-Type': 'application/json'})


@app.route('/v1/images', methods=['DELETE'])
def remove_file():
    params = check_params()

    def remove_object():
        for item in items:
            table.delete_item(Key={
                'userId': params['userId'],
                'fileId': item.get('fileId')
            })
            s3.delete_object(Bucket=bucket, Key=item.get('fileName'))

    if set(params.keys()) == {'userId', 'collectionId', 'position'}:
        items = get_item(params['userId'], params['collectionId'], params['position'])
    elif set(params.keys()) == {'userId', 'collectionId'}:
        items = get_item(params['userId'], params['collectionId'])
    else:
        raise BadRequestError('Wrong parameters')

    try:
        remove_object()
        reorganize_items(params['userId'], params['collectionId'])
    except Exception:
        raise BadRequestError("Can't remove file")

    return Response(body={'message': 'Collection/file has been removed'},
                    status_code=200,
                    headers={'Content-Type': 'application/json'})
