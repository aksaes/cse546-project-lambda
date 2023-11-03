import boto3
import face_recognition
import pickle
import urllib
import os
import numpy as np
import json

input_bucket = "input-bucket-zxz"
output_bucket = "output-bucket-zxz"

s3 = boto3.resource('s3')
dynamodb = boto3.resource('dynamodb')

table = dynamodb.Table('Student-Data')

# Function to read the 'encoding' file
def open_encoding(filename):
	file = open(filename, "rb")
	data = pickle.load(file)
	file.close()
	return data

def get_DBitem(item):
	try:
		response = table.get_item(
			Key={
				'name': item
			},
			ProjectionExpression='#n, major, #yr',
			ExpressionAttributeNames={
				'#n': 'name',
				'#yr': 'year'
			}
    	)
		if 'Item' in response:
			print('Item found:', response['Item'])
			return response['Item']
		else:
			print('No item found with the primary key:', primary_key_value)
			return -1
	except Exception as e:
		print('Error fetching item from DynamoDB: ', e)
		return -1

def face_recognition_handler(event, context):	
	bucket = event['Records'][0]['s3']['bucket']['name']
	key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding = 'utf-8')
	input_bucket = s3.Bucket(bucket)
	obj = input_bucket.Object(key)
	obj.download_file(key)

	# key = 'test_cases/test_case_1/test_1.mp4'
	# print('ffmpeg -i {} -r 1 {} -y'.format(key, key.split('.')[0] + '.jpeg'))
	
	os.system('ffmpeg -i {} -r 1 {} -y'.format(key, key.split('.')[0] + '.jpeg'))

	img = face_recognition.load_image_file(key.split('.')[0] + '.jpeg')
	face_encoding = face_recognition.face_encodings(img)[0]
	
	encodings = open_encoding('encoding')
	scores = face_recognition.api.face_distance(encodings['encoding'], face_encoding)
	match_idx = np.argmin(scores)
	match_name = encodings['name'][match_idx]

	# Fetch record from DB
	item = get_DBitem(match_name)

	if item == -1:
		return

	print(item)

	# Output to S3
	item_string = json.dumps(item)

	s3_output_key = key.split('/')[-1].split('.')[0]
	s3.Bucket(output_bucket).put_object(Key=s3_output_key, Body=item_string)

	print(f"Response has been uploaded to '{output_bucket}' as '{s3_output_key}'.")