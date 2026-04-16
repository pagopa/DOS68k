from pydantic import SecretStr


class AWSCredentialsSettingsMock:
    AWS_ACCESS_KEY_ID: str = "mock-access-key"
    AWS_SECRET_ACCESS_KEY: SecretStr = SecretStr("mock-secret-key")

def get_aws_credentials_settings_mock() -> AWSCredentialsSettingsMock:
    return AWSCredentialsSettingsMock()
