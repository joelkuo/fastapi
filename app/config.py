from pydantic_settings import BaseSettings
import os
class Settings(BaseSettings):
    """
    Application configuration settings using Pydantic BaseSettings.
    
    BaseSettings vs BaseModel:
    - BaseModel: Regular data validation (API requests/responses)
    - BaseSettings: Configuration management with automatic environment variable support
    
    How BaseSettings works:
    1. First looks for environment variables (e.g., DATABASE_PASSWORD)
    2. Falls back to default values if no env var is found
    3. Raises error if required field has no default and no env var
    
    Environment variable priority (highest to lowest):
    1. Environment variables (e.g., export DATABASE_PASSWORD="secret")
    2. .env file variables
    3. Default values specified in the class
    
    Example environment variables:
    export DATABASE_PASSWORD="your_prod_password"
    export DATABASE_URL="prod-server.com"
    export SECRET_KEY="your_production_secret"
    
    Usage:
    settings = Settings()  # Automatically reads from environment + defaults
    print(settings.database_url)  # "localhost" (default) or env value
    """
    
    # Database configuration
    database_hostname: str 
    database_password: str
    #if we keep no default value, it will go check the local machine's environment variable, raise an error if the environment variable is not set
    database_username: str
    database_name: str
    database_port: str
    
    # JWT authentication configuration
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    class Config:
        env_file = ".env"
settings = Settings()
# print(settings.database_hostname)