import os
import boto3

#initiate s3 resource
s3 = boto3.resource('s3')

# select bucket
my_bucket = s3.Bucket('output-bucket-zxz')

# download file into current directory
for s3_object in my_bucket.objects.all():
    # Need to split s3_object.key into path and file name, else it will give error file not found.
    path, filename = os.path.split(s3_object.key)
    my_bucket.download_file(s3_object.key, filename)