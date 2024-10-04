import os
import shutil
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from pathlib import Path
from uuid import uuid4

import pandas as pd
from faker import Faker
from fire import Fire
from sqlalchemy import create_engine

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
    cache_dir: Path,
) -> ...:
    logger.info(f"Generating {n} number of users")
    fake = Faker(locale="en_US")

    users = []
    for _ in range(n):
        users.append(_generate_user(fake=fake))

    table = pd.DataFrame([asdict(user) for user in users])

    _output_path: Path = cache_dir / f"{uuid4()}.parquet"

    table.to_parquet(_output_path, engine="pyarrow")
    logger.info(f"Successfully generated {n} users. Stored as: {_output_path}")


def main(tasks: int, amount: int) -> ...:
    logger.info(f"Will generate {amount} of users")

    _cache_dir: Path = Path(__file__).parents[1] / ".cache"
    if _cache_dir.exists():
        shutil.rmtree(_cache_dir)
    _cache_dir.mkdir()

    logger.info(f"Submiting {tasks} tasks")
    with ProcessPoolExecutor(max_workers=tasks) as executor:
        futures = [
            executor.submit(
                generate_users_data,
                n=round(amount / tasks),
                cache_dir=_cache_dir,
            )
            for _ in range(tasks)
        ]
    for future in as_completed(futures):
        output = future.result()
        if output:
            logger.warning(f"Got output from process: {output}")
    logger.info("All tasks finished successfully")

    logger.info(f"Creating table based on files in {_cache_dir}")
    table: pd.DataFrame = pd.concat(
        [pd.read_parquet(_cache_dir / file) for file in os.listdir(_cache_dir)]
    )
    logger.debug("Table shape is %s", table.shape)

    _certs_dir = Path(__file__).parents[1] / "certs"
    logger.info(f"Initializing database engine. Using SSL certs from {_certs_dir}")

    engine = create_engine(
        url=DB_URL,
        connect_args={
            "sslmode": "require",
            "sslrootcert": _certs_dir / "ca.crt",
            "sslcert": _certs_dir / "client.crt",
            "sslkey": _certs_dir / "client.key",
        },
    )

    _dbtable = "public.users"
    logger.info(f"Inserting data into {_dbtable} database table")

    with engine.connect() as conn:
        table.to_sql(
            schema=_dbtable.split(".")[0],
            name=_dbtable.split(".")[1],
            index=False,
            con=conn,
            if_exists="append",
        )
    logger.info("Inserted all data successfully")
    shutil.rmtree(_cache_dir)


if __name__ == "__main__":
    try:
        Fire(main)
    except Exception as err:
        logger.exception(err)
        sys.exit(1)
