from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr
from os import path


class Settings(BaseSettings):
    host: SecretStr
    port: SecretStr
    model_config = SettingsConfigDict(env_file=str(path.dirname(path.abspath(__file__)) + path.sep + '.env'),
                                      env_file_encoding='utf-8')


config = Settings()
