"""
Configuration management for Kansofy-Trade
"""

import os
from pathlib import Path
from typing import List
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    # Database
    database_url: str = f"sqlite:///{os.getenv('DATABASE_PATH', './kansofy_trade.db')}"
    database_path: str = os.getenv("DATABASE_PATH", "./kansofy_trade.db")
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    
    # MCP Server
    mcp_server_port: int = 8001
    mcp_server_host: str = "localhost"
    
    # Document Processing
    upload_dir: str = os.getenv("UPLOAD_PATH", "./uploads")
    max_file_size: int = 50 * 1024 * 1024  # 50MB
    allowed_extensions: List[str] = ["pdf", "docx", "txt", "xlsx", "csv"]
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    
    # CORS
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000"
    ]
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Optional AI Services
    anthropic_api_key: str = ""
    openai_api_key: str = ""
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return not self.debug
    
    @property
    def upload_path(self) -> Path:
        """Get upload directory as Path object"""
        return Path(self.upload_dir)
    
    def get_allowed_extensions_set(self) -> set:
        """Get allowed file extensions as a set"""
        return {ext.lower().strip('.') for ext in self.allowed_extensions}


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()