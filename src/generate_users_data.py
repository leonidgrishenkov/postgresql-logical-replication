import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from pathlib import Path

from faker import Faker
from fire import Fire
from sqlalchemy import create_engine, text
from sqlalchemy.engine.base import Connection

from utils import DB_URL, logger


@dataclass
class User:
    first_name: str
    last_name: str
    gender: str
    email: str
    country: str
    address: str
    ip_address: str
    phone_number: str


def _generate_user(fake: Faker) -> User:
    gender = fake.random_element(elements=("Male", "Female"))

    return User(
        first_name=fake.first_name_male() if gender == "Male" else fake.first_name_female(),
        last_name=fake.last_name_male() if gender == "Female" else fake.last_name_female(),
        gender=gender,
        email=fake.email(),
        country=fake.country(),
        address=fake.address(),
        ip_address=fake.ipv4(),
        phone_number=fake.phone_number(),
    )


def generate_users_data(
    n: int,
    fake: Faker,
    query: str,
) -> ...:
    logger.info(f"Generating {n} number of users")

    engine = create_engine(
        url=DB_URL,
        connect_args={
            "sslmode": "require",
            "sslrootcert": Path(__file__).parents[1] / "certs/ca.crt",
            "sslcert": Path(__file__).parents[1] / "certs/client.crt",
            "sslkey": Path(__file__).parents[1] / "certs/client.key",
        },
    )
    conn: Connection = engine.connect()

    for _ in range(n):
        _user: User = _generate_user(fake=fake)
        conn.execute(text(query), asdict(_user))
        conn.commit()

    conn.close()
    logger.info(f"Successfully inserted {n} usert into database table")


def main(tasks: int, amount: int) -> ...:
    fake = Faker(locale="en_US")

    logger.info(f"Will generate {amount} of users")

    sqlfile: Path = Path(__file__).parents[0] / "sql/insert/users.sql"
    logger.info(f"Reading sql file: {sqlfile}")
    query: str = sqlfile.read_text()

    logger.info(f"Submiting {tasks} tasks")
    with ProcessPoolExecutor(max_workers=tasks) as executor:
        futures = [
            executor.submit(
                generate_users_data,
                n=round(amount / tasks),
                fake=fake,
                query=query,
            )
            for _ in range(tasks)
        ]
    for future in as_completed(futures):
        output = future.result()
        if output:
            logger.warning(f"Got output from process: {output}")

    logger.info("All tasks finished successfully")


if __name__ == "__main__":
    try:
        Fire(main)
    except Exception as err:
        logger.exception(err)
        sys.exit(1)
