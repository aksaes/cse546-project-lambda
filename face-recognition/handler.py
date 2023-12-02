import os
import subprocess
import pickle
import face_recognition
import boto3
import numpy as np
import urllib
import json

print('handler start')
input_bucket = "input-bucket"
output_bucket = "output-bucket"

s3_session = boto3.Session(profile_name='s3api')
s3 = s3_session.resource(
	service_name = 's3',
	endpoint_url = 'http://10.0.2.15:8081',
	)

dynamodb_session = boto3.Session(profile_name='dynamodb')

dynamodb = dynamodb_session.resource(
	service_name = 'dynamodb',
	)

table = dynamodb.Table('student_data')

# def face_recognition_handler(req):
#     """Handles the incoming request to process the video"""

#     bucket = req['Records'][0]['s3']['bucket']['name']
#     key = urllib.parse.unquote_plus(req['Records'][0]['s3']['object']['key'], encoding = 'utf-8')
#     input_bucket = s3.Bucket(bucket)
#     obj = input_bucket.Object(key)
#     obj.download_file('/tmp/' + key)
    
#     extract_frames(key)

#     # Recognize faces from the first frame
#     img = os.path.join('/tmp/', key.split('.')[0] + '.jpeg')
#     match_name = recognize_face('/tmp/' + img)

#     # Query DynamoDB for academic information
#     academic_info = get_DBitem(match_name)

#     if academic_info == -1:
#         return

#     # Output the academic information
#     print(academic_info)
#     item_string = f"{academic_info['name']}, {academic_info['major']}, {academic_info['year']}"
    
#     s3_output_key = f"{key.split('/')[-1].split('.')[0]}.txt"
#     s3.Bucket(output_bucket).put_object(Key=s3_output_key, Body=item_string)
    
#     print(f"Response has been uploaded to '{output_bucket}' as '{s3_output_key}'.")
    
# def extract_frames(filename):
#     """Extracts frames from the video using ffmpeg"""
#     try:
#         subprocess.check_call(
#             ['ffmpeg', '-i', '/tmp/' + filename, '-r', '1', '/tmp/' + filename.split('.')[0] + ".jpeg"]
#         )
#     except subprocess.CalledProcessError as e:
#         print('Failed to extract frames from video', e)

def open_encoding(filename):
    file = open(filename, "rb")
    data = pickle.load(file)
    file.close()
    return data

# def recognize_face(image_path):
#     """Recognize the first face in the image using face_recognition"""
#     image = face_recognition.load_image_file(image_path)

#     # Find all face encodings in the image
#     face_encoding = face_recognition.face_encodings(image)[0]
#     # first_face_encoding = face_encodings[0]

#     encodings = open_encoding('encoding')
#     scores = face_recognition.api.face_distance(encodings['encoding'], face_encoding)
#     match_idx = np.argmin(scores)
#     match_name = encodings['name'][match_idx]

#     return match_name

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
			print('No item found with the primary key:', item)
			return -1
	except Exception as e:
		print('Error fetching item from DynamoDB: ', e)
		return -1

def face_recognition_handler(event, context):
	print('Starting face_recognition_handler')
	# bucket = event['Records'][0]['s3']['bucket']['name']
	# key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding = 'utf-8')
	str_data = event.body.decode('utf8').replace("'", '"')
	parsed_data = urllib.parse.parse_qs(str_data)
	req = {key: value[0] for key, value in parsed_data.items()}
	# print(req)
	bucket, key = (req['bucket'], req['key'])
	input_bucket = s3.Bucket(bucket)
	obj = input_bucket.Object(key)
	print('Starting file download from ceph')
	obj.download_file('/tmp/' + key)
	print('Finished file download from ceph')
	# key = 'test_cases/test_case_1/test_1.mp4'
	# print('ffmpeg -i {} -r 1 {} -y'.format(key, key.split('.')[0] + '.jpeg'))
	
	os.system('ffmpeg -i {} -r 1 {} -y'.format('/tmp/' + key, '/tmp/' + key.split('.')[0] + '.jpeg'))
	# raise Exception('test1')

	print('Starting image recognition')
	img = face_recognition.load_image_file('/tmp/' + key.split('.')[0] + '.jpeg')
	face_encoding = face_recognition.face_encodings(img)[0]
	raise Exception('testFace_Encodings')
	
	encodings = open_encoding('encoding')
	scores = face_recognition.api.face_distance(encodings['encoding'], face_encoding)
	raise Exception('test2')
	match_idx = np.argmin(scores)
	match_name = encodings['name'][match_idx]
	print('Finished face recognition')
	print('Get record from DB')
	# Fetch record from DB
	item = get_DBitem(match_name)
	raise Exception('test3')
	print('Got record from DB')
	if item == -1:
		print('Some error fetching record from DB')
		return

	print(item)

	# Output to S3
	item_string = f"{item['name']}, {item['major']}, {item['year']}"

	s3_output_key = f"{key.split('/')[-1].split('.')[0]}.txt"
	print('Uploading to S3')
	s3.Bucket(output_bucket).put_object(Key=s3_output_key, Body=item_string)
	raise Exception('test4')
	print('Uploaded to S3')
	print(f"Response has been uploaded to '{output_bucket}' as '{s3_output_key}'.")
	raise Exception('test')
