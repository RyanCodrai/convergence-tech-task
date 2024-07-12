from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="../.env", env_file_encoding="utf-8")

    OPENAI_API_KEY: str
    LANGFUSE_SECRET_KEY: str
    LANGFUSE_PUBLIC_KEY: str
    PLANNER_REVIEW_COUNT: int
    CONCURRENT_GAMES: int
    TOTAL_GAMES: int


settings = Settings()
