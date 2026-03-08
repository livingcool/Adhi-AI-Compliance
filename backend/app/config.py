import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, AnyHttpUrl, model_validator
from pathlib import Path
from enum import Enum
from typing import Optional

# --- Enums for Settings ---

class StorageBackend(str, Enum):
    LOCAL = "local"
    S3 = "s3"

class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"

class LLMProvider(str, Enum):
    OPENAI = "openai"
    GEMINI = "gemini"
    HUGGINGFACE = "huggingface"  # Open-source models via HF Inference API
    BEDROCK = "bedrock"  # Amazon Bedrock (Claude, Titan)

# --- Main Settings Class ---

class Settings(BaseSettings):
    """
    Validates and loads all environment variables for the application.
    """

    # --- App ---
    APP_NAME: str = "Adhi Compliance"
    APP_VERSION: str = "1.0.0"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    LOG_LEVEL: LogLevel = LogLevel.INFO
    # Default allowed origins — override with ALLOWED_ORIGINS env var (comma-separated)
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:5173", "http://localhost:8080"]

    # --- Storage ---
    STORAGE_BACKEND: StorageBackend = StorageBackend.LOCAL
    STORAGE_LOCAL_ROOT: Path = Field(default=Path("./data"))
    DATABASE_URL: str = "sqlite:///./data/metadata.db"

    # --- Sarvam ---
    SARVAM_API_KEY: str = Field(default="", env="SARVAM_API_KEY")
    SARVAM_API_URL: str = Field("https://api.sarvam.ai/stt", env="SARVAM_API_URL")

    # --- Redis / Celery (Optional for HF Spaces) ---
    REDIS_URL: Optional[str] = Field(None, env="REDIS_URL")
    CELERY_BROKER_URL: Optional[str] = Field(None, validation_alias="REDIS_URL")
    CELERY_RESULT_BACKEND: Optional[str] = Field(None, validation_alias="REDIS_URL")
    CELERY_DEFAULT_QUEUE: str = "cpu_tasks"

    # --- File Upload Limits ---
    MAX_UPLOAD_SIZE_MB: int = 500
    UPLOAD_CHUNK_SIZE_BYTES: int = 1024 * 1024  # 1MB chunks

    # --- Celery Task Timeouts ---
    CELERY_TASK_TIME_LIMIT: int = 3600  # 1 hour
    CELERY_TASK_SOFT_TIME_LIMIT: int = 3300  # 55 minutes warning

    # --- Embeddings / LLM ---
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    LLM_PROVIDER: LLMProvider = LLMProvider.GEMINI  # Default to open-source

    OPENAI_API_KEY: Optional[str] = Field(None, description="Required if LLM_PROVIDER is 'openai'")
    GOOGLE_API_KEY: Optional[str] = Field(None, description="Required if LLM_PROVIDER is 'gemini'")

    # --- HuggingFace ---
    HF_TOKEN: Optional[str] = Field(None, description="HuggingFace API token (optional, but recommended for higher rate limits)")
    HF_MODEL_CHAT: str = Field("mistralai/Mixtral-8x7B-Instruct-v0.1", description="HuggingFace model for chat/QA")
    HF_MODEL_EMBED: str = Field("sentence-transformers/all-MiniLM-L6-v2", description="HuggingFace model for embeddings")

    # --- Supabase (legacy — being replaced by AWS RDS) ---
    SUPABASE_URL: Optional[str] = Field(None, env="SUPABASE_URL")
    SUPABASE_SERVICE_ROLE_KEY: Optional[str] = Field(None, env="SUPABASE_SERVICE_ROLE_KEY")
    SUPABASE_ANON_KEY: Optional[str] = Field(None, env="SUPABASE_ANON_KEY")
    # JWT secret from: Supabase Dashboard > Settings > API > JWT Settings > JWT Secret
    SUPABASE_JWT_SECRET: Optional[str] = Field(None, env="SUPABASE_JWT_SECRET")

    # --- AWS Core ---
    AWS_REGION: str = Field("ap-south-1", env="AWS_REGION")
    AWS_ACCESS_KEY_ID: Optional[str] = Field(None, env="AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: Optional[str] = Field(None, env="AWS_SECRET_ACCESS_KEY")

    # --- Amazon S3 ---
    AWS_S3_BUCKET: Optional[str] = Field(None, env="AWS_S3_BUCKET")
    AWS_S3_PRESIGNED_URL_EXPIRY: int = Field(3600, env="AWS_S3_PRESIGNED_URL_EXPIRY")  # seconds

    # --- Amazon Bedrock ---
    AWS_BEDROCK_REGION: str = Field("ap-south-1", env="AWS_BEDROCK_REGION")
    AWS_BEDROCK_CHAT_MODEL_ID: str = Field(
        "anthropic.claude-3-5-sonnet-20241022-v2:0",
        env="AWS_BEDROCK_CHAT_MODEL_ID",
        description="Bedrock model ID for chat/RAG generation",
    )
    AWS_BEDROCK_EMBED_MODEL_ID: str = Field(
        "amazon.titan-embed-text-v2:0",
        env="AWS_BEDROCK_EMBED_MODEL_ID",
        description="Bedrock model ID for text embeddings",
    )

    # --- Amazon Cognito (replaces Supabase Auth — optional) ---
    AWS_COGNITO_USER_POOL_ID: Optional[str] = Field(None, env="AWS_COGNITO_USER_POOL_ID")
    AWS_COGNITO_APP_CLIENT_ID: Optional[str] = Field(None, env="AWS_COGNITO_APP_CLIENT_ID")

    # --- Amazon ElastiCache (drop-in Redis replacement) ---
    # Just set REDIS_URL to point at ElastiCache endpoint — no code change needed

    # --- CORS ---
    # Comma-separated list of allowed origins; overrides CORS_ORIGINS when set.
    # Example: "http://localhost:3000,https://app.example.com"
    ALLOWED_ORIGINS: Optional[str] = Field(None, env="ALLOWED_ORIGINS")

    # --- Alert Channels ---
    ALERT_SLACK_WEBHOOK: Optional[str] = Field(None, description="Slack incoming webhook URL for compliance alerts")
    ALERT_EMAIL_SMTP: Optional[str] = Field(None, description="SMTP DSN for email alerts, e.g. smtp://user:pass@host:587")
    ALERT_EMAIL_FROM: str = Field("alerts@adhi-compliance.ai", description="Sender address for email alerts")
    ALERT_TEAMS_WEBHOOK: Optional[str] = Field(None, description="Microsoft Teams incoming webhook URL for alerts")

    # --- Compliance Monitoring ---
    COMPLIANCE_SCAN_INTERVAL_HOURS: int = Field(24, description="Hours between automated compliance scans")

    # --- App Limits (Tuning) ---
    VIDEO_FRAME_INTERVAL_SEC: int = 7
    TRANSCRIPT_CHUNK_SEC: int = 30
    BATCH_EMBED_SIZE: int = 16

    # --- Derived Paths (Computed properties) ---
    @property
    def UPLOAD_DIR(self) -> Path:
        return self.STORAGE_LOCAL_ROOT / "uploads"

    @property
    def TRANSCRIPT_DIR(self) -> Path:
        return self.STORAGE_LOCAL_ROOT / "transcripts"

    @property
    def FRAME_DIR(self) -> Path:
        return self.STORAGE_LOCAL_ROOT / "frames"

    @property
    def VECTOR_DIR(self) -> Path:
        return self.STORAGE_LOCAL_ROOT / "vectors"

    @model_validator(mode="after")
    def apply_allowed_origins(self) -> "Settings":
        """If ALLOWED_ORIGINS env var is set, parse it and override CORS_ORIGINS."""
        if self.ALLOWED_ORIGINS:
            parsed = [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]
            if parsed:
                self.CORS_ORIGINS = parsed
        return self

    # --- Model Config ---
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

# --- Singleton Instance ---
try:
    settings = Settings()

    # --- Global LLM Initialization ---
    if settings.LLM_PROVIDER == LLMProvider.GEMINI:
        if not settings.GOOGLE_API_KEY:
            raise ValueError("LLM_PROVIDER is set to GEMINI, but GOOGLE_API_KEY is missing.")

    elif settings.LLM_PROVIDER == LLMProvider.HUGGINGFACE:
        if not settings.HF_TOKEN:
            print("[WARN] HF_TOKEN not set. Using public HuggingFace inference (rate limited).")

    elif settings.LLM_PROVIDER == LLMProvider.BEDROCK:
        if not settings.AWS_ACCESS_KEY_ID or not settings.AWS_SECRET_ACCESS_KEY:
            print("[WARN] AWS_ACCESS_KEY_ID/SECRET not set — Bedrock will use IAM instance role.")

    print(f"[CONFIG] LLM Provider : {settings.LLM_PROVIDER.value}")
    print(f"[CONFIG] Storage      : {settings.STORAGE_BACKEND.value}")
    if settings.STORAGE_BACKEND.value == "s3":
        print(f"[CONFIG] S3 Bucket    : {settings.AWS_S3_BUCKET}")

except Exception as e:
    print(f"FATAL: Error loading configuration. {e}")
    raise

# --- Helper Function ---
def get_settings() -> Settings:
    """Dependency for FastAPI to get the settings."""
    return settings
