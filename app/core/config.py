from pydantic_settings import BaseSettings, SettingsConfigDict

class Setting(BaseSettings):

    db_url: str
    db_host_name: str
    db_port: int
    db_name: str
    db_password: str

    mq_url: str
    mq_port: str
    mq_user: str

    model_config = SettingsConfigDict(
        env_file=".env.dev",
        env_file_encoding="utf-8",
        extra="ignore"
    )

setting = Setting()
