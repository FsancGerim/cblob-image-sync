import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

# SQL SERVER
SQL_SERVER = os.getenv("ZP_SQL_SERVER")
SQL_DB = os.getenv("ZP_SQL_DB")
SQL_USER = os.getenv("ZP_SQL_USER")
SQL_PASS = os.getenv("ZP_SQL_PASS")
SQL_DRIVER = os.getenv("ZP_SQL_DRIVER")

# NAS
NAS_FOLDER = Path(os.getenv("NAS_FOLDER"))
TEST_OUTPUT_FOLDER = Path(os.getenv("TEST_OUTPUT_FOLDER", ""))

# LOGS
RESULT_LOG_FILE = Path("logs/sync_results.log")
CLEANUP_LOG_FILE = Path("logs/cleanup_results.log")

# SMB
NAS_SHARE = os.environ.get("NAS_SHARE")  
NAS_USER = os.environ.get("NAS_USER")
NAS_PASS = os.environ.get("NAS_PASS")

# CORREO
MAIL_TO = os.getenv("MAIL_TO", "").split(",")
MAIL_FROM = os.getenv("MAIL_FROM")
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")