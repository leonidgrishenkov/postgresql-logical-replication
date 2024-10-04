import logging
import os
import sys

logging.basicConfig(
    level=logging.DEBUG,
    format=r"[%(asctime)s] {%(process)d.%(module)s.%(funcName)s:%(lineno)d} %(levelname)s: %(message)s",
    datefmt=r"%Y-%m-%d %H:%M:%S",
    stream=sys.stdout,
)
logger = logging.getLogger()

user = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")
host = os.getenv("POSTGRES_HOST")
port = os.getenv("POSTGRES_PORT")
db = os.getenv("POSTGRES_DB")

DB_URL = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"
