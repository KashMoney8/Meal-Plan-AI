from pydantic import BaseSettings
import os

class Settings(BaseSettings):
    FLASK_ENV: str = 'development'
    SECRET_KEY: str = 'dev'
    JWT_SECRET: str = 'devjwt'

    DATABASE_URL: str = 'postgresql+psycopg2://postgres:postgres@db:5432/mealplanner'

    # Vertex AI
    GOOGLE_CLOUD_PROJECT: str = ''
    VERTEX_LOCATION: str = 'us-central1'
    VERTEX_MODEL: str = 'gemini-1.5-pro'
    VERTEX_EMBED_MODEL: str = 'text-embedding-004'
    GOOGLE_APPLICATION_CREDENTIALS: str = '/secrets/gcp-sa.json'

    # Pinecone
    PINECONE_API_KEY: str = ''
    PINECONE_ENV: str = 'us-east-1'
    PINECONE_INDEX: str = 'recipes-idx'
    PINECONE_NAMESPACE: str = 'default'

    DEFAULT_UNITS: str = os.environ.get('DEFAULT_UNITS', 'us')

    class Config:
        env_file = '.env'
