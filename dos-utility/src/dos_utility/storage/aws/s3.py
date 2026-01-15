from boto3 import client as AWSClient

from .env import aws_storage_settings

class AWSS3():
    def __init__(self):
        if aws_storage_settings.s3_endpoint is not None:
            self.client: AWSClient = AWSClient(
                "s3",
                region_name=aws_storage_settings.aws_region,
                endpoint_url=aws_storage_settings.s3_endpoint,
                aws_access_key_id=aws_storage_settings.aws_access_key_id,
                aws_secret_access_key=aws_storage_settings.aws_secret_access_key,
            )
        else:
            self.client: AWSClient = AWSClient("s3", region_name=aws_storage_settings.aws_region)

    def health_check(self, bucket_name: str=aws_storage_settings.bucket_name) -> None:
        # Simple health check to verify S3 connectivity
        self.client.head_bucket(Bucket=bucket_name)
