import os

# Mock env variables
os.environ["S3_ENDPOINT"] = "http://storage:9000"
os.environ["BUCKET_NAME"] = "chatbot-index"
os.environ["AWS_ACCESS_KEY_ID"] = "admin"
os.environ["AWS_SECRET_ACCESS_KEY"] = "minioadmin"
os.environ["AWS_REGION"] = "us-west-1"