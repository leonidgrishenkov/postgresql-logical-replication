import sys
from pathlib import Path

from sqlalchemy import create_engine, text

from utils import DB_URL, logger


def main() -> ...:
    sqlfile: Path = Path(__file__).parents[0] / "sql/ddl/users.sql"
    logger.info(f"Reading sql file: {sqlfile}")
    query: str = sqlfile.read_text()

    engine = create_engine(
        url=DB_URL,
        connect_args={
            "sslmode": "require",
            "sslrootcert": Path(__file__).parents[1] / "certs/ca.crt",
            "sslcert": Path(__file__).parents[1] / "certs/client.crt",
            "sslkey": Path(__file__).parents[1] / "certs/client.key",
        },
    )
    logger.info("Executing DDL query")
    with engine.connect() as conn:
        conn.execute(text(query))
        conn.commit()

    logger.info('Successfully executed DDL query')

if __name__ == "__main__":
    try:
        main()
    except Exception as err:
        logger.exception(err)
        sys.exit(1)
