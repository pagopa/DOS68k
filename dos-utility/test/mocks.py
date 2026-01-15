class AWSClientMock:
    # Mock AWS S3 client for testing
    def __init__(self, *args, **kwargs):
        return

    def head_bucket(self, *args, **kwargs) -> None:
        return

class AWSClientExceptionMock(AWSClientMock):
    def head_bucket(self, *args, **kwargs) -> None:
        raise Exception("Mocked storage connection error")

class AWSStorageSettingsMock:
    s3_endpoint = "http://storage:9000"
    bucket_name = "chatbot-index"
    aws_access_key_id = "admin"
    aws_secret_access_key = "minioadmin"
    aws_region = "us-west-1"
