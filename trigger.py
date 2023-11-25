import boto3

boto3.setup_default_session(profile_name = 's3api')

input_bucket_name = 'input-bucket'
output_bucket_name = 'output-bucket'
s3 = boto3.client('s3', endpoint_url = 'http://10.0.2.15:8081')

curr_len = 0

get_last_modified = lambda obj: int(obj['LastModified'].strftime('%s'))



def trigger_lambda(bucket, new_obj_key):
    print(bucket, new_obj_key)


if __name__ == '__main__':
    global curr_len

    while True:
        objs = list(s3.list_objects_v2(Bucket=input_bucket_name)['Contents'])
        new_len = len(objs)

        if new_len != curr_len:
            curr_len = new_len
            new_obj_keys = [obj['Key'] for obj in sorted(objs, key = get_last_modified)][curr_len: new_len]

            for new_obj_key in new_obj_keys:
                trigger_lambda(input_bucket_name, new_obj_key)