import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-key-change-in-production"
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL"
    ) or "sqlite:///" + os.path.join(basedir, "database", "tubans.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Pagination
    TUBANS_PER_PAGE = 20

    # Upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.path.join(basedir, "uploads")

    # Excel settings
    EXCEL_ALLOWED_EXTENSIONS = {"xlsx", "xls"}

    # Application settings
    APP_NAME = "地质公园疑似违法图斑管理系统"
    APP_VERSION = "1.0.0"

    # Cache settings (seconds)
    STATS_CACHE_TTL = int(os.environ.get("STATS_CACHE_TTL", 30))
    MAP_CACHE_TTL = int(os.environ.get("MAP_CACHE_TTL", 15))

    # Date format
    DATE_FORMAT = "%Y-%m-%d"
    DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
