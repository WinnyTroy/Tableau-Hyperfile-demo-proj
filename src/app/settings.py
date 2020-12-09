from pydantic import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Demo data visualization integration with Tableau"
    app_description: str = ""
    app_version: str = "0.0.1"
    redis_cache_url: str = "redis://cache"
    # Generate secret key using:
    #  dd if=/dev/urandom bs=32 count=1 2>/dev/null | openssl base64
    secret_key: str = "xLLwpyLgT0YumXu77iDYX+HDVBX6djFFVbAWPhhHAHY="
    media_path: str = "/home/winny/demo_proj/src/app"
    s3_bucket: str = "TableauhyperDemo"
    # For more on tokens, head here:
    # https://help.tableau.com/current/server/en-us/security_personal_access_tokens.htm
    tableau_server_address: str = ""
    tableau_site_name: str = ""
    tableau_token_name: str = ""
    tableau_token_value: str = ""


settings = Settings()