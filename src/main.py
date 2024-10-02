import logging
import os
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from pathlib import Path

from faker import Faker
from sqlalchemy import create_engine, text
from sqlalchemy.engine.base import Connection

logging.basicConfig(
    level=logging.INFO,
    format=r"[%(asctime)s] {%(module)s.%(funcName)s:%(lineno)d} %(levelname)s: %(message)s",
    datefmt=r"%Y-%m-%d %H:%M:%S",
    stream=sys.stdout,
)
log = logging.getLogger()


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
    log.info(f"Generating {n} number of users")

    user = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    host = os.getenv("VM_SOURCE_EXT_IP")
    # TODO: Set these into env.sh and add to terraform.
    port = os.getenv("POSTGRES_PORT")
    db = os.getenv("POSTGRES_DB")

    engine = create_engine(
        url=f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}",
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
    log.info(f"Successfully inserted {n} usert into database table")


def main() -> ...:
    fake = Faker(locale="en_US")

    sqlfile: Path = Path(__file__).parents[0] / "sql/insert/users.sql"
    query: str = sqlfile.read_text()

    tasks: int = 4
    log.info(f"Submiting {tasks} tasks")

    with ProcessPoolExecutor(max_workers=tasks) as executor:
        futures = [
            executor.submit(
                generate_users_data,
                n=1_000_000,
                fake=fake,
                query=query,
            )
            for _ in range(tasks)
        ]
    for future in as_completed(futures):
        output = future.result()
        if output:
            log.warning(f"Got output from process: {output}")


if __name__ == "__main__":
    try:
        main()
    except Exception as err:
        log.exception(err)
        sys.exit(1)
