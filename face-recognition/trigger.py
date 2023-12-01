import boto3
import requests

boto3.setup_default_session(profile_name = 's3api')

print('Trigger started')

input_bucket_name = 'input-bucket'
output_bucket_name = 'output-bucket'

s3 = boto3.client('s3',
    endpoint_url = 'http://10.0.2.15:8081',
)

curr_len = 0

get_last_modified = lambda obj: int(obj['LastModified'].strftime('%s'))



def trigger_lambda(bucket, new_obj_key):
    print('In trigger_lambda')
    print(bucket, new_obj_key)
    openfaas_url = 'http://localhost:31112/function/face-recognition'
    payload = {
        'bucket': bucket,
        'key': new_obj_key
    }

    try:
        requests.post(url = openfaas_url, data = payload, timeout = 0.1)
    except:
        pass
    print('After request post in trigger_lambda')

while True:
    print('Inside loop')
    objs = list(s3.list_objects_v2(Bucket=input_bucket_name)['Contents'])
    new_len = len(objs)

    if new_len != curr_len:
        new_obj_keys = [obj['Key'] for obj in sorted(objs, key = get_last_modified)][curr_len: new_len]

        for new_obj_key in new_obj_keys:
            trigger_lambda(input_bucket_name, new_obj_key)
        
        curr_len = new_len
