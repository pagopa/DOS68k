"""Settings module for the authentication service."""
from typing import Annotated, Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    
    # Authentication Provider Configuration
    auth_provider: Annotated[
        str, 
        Field(default="cognito", description="Authentication provider type (cognito, keycloak, etc.)")
    ]
    
    # AWS Cognito Settings
    aws_region: Annotated[
        Optional[str], 
        Field(default=None, description="AWS region")
    ]
    aws_cognito_region: Annotated[
        Optional[str], 
        Field(default=None, description="AWS Cognito specific region")
    ]
    auth_cognito_userpool_id: Annotated[
        Optional[str], 
        Field(default=None, description="AWS Cognito User Pool ID")
    ]
    aws_endpoint_url: Annotated[
        Optional[str], 
        Field(default=None, description="AWS endpoint URL for local testing")
    ]
    
    # Keycloak Settings (optional, only needed if using keycloak provider)
    keycloak_url: Annotated[
        Optional[str], 
        Field(default=None, description="Keycloak server URL")
    ]
    keycloak_realm: Annotated[
        Optional[str], 
        Field(default=None, description="Keycloak realm name")
    ]
    
    # Environment
    environment: Annotated[
        str, 
        Field(default="production", description="Environment (test, development, production)")
    ]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
SETTINGS = Settings()
