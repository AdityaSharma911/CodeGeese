from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    mongo_uri: str
    mongo_db_name: str
    qdrant_host: str
    qdrant_collection_name: str
    qdrant_api_key:str
    leetcode_session:str
    leetcode_csrf_token:str

    class Config:
        env_file = "src/.env"

settings = Settings()
