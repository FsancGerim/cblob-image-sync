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