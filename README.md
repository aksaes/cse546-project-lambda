# cse546-project-lambda

Cloud Computing Project 2

These are the instructions to run the project.

1. Run the `workload_generator.py` script to upload the test case videos to input bucket `input-bucket-zxz` . The trigger setup will automatically call the lambda function which would process the file and give the output in the output bucket, for each file.

2. After logging in to AWS, check the output bucket `output-bucket-zxz` to get the output related to each testcase.
