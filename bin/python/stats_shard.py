import contextlib
import datetime
import random
import sqlite3
import sqlite_utils
import uuid

import faker

DATABASE = "./var/stats.db"
SCHEMA = "./share/stats.sql"

NUM_STATS = 1_000_000
NUM_USERS = 100_000
YEAR = 2022

random.seed(YEAR)
fake = faker.Faker()
fake.seed(YEAR)

DATABASE = "./var/stats_full.db"
SCHEMA = "./share/stats.sql"

sqlite3.register_converter("GUID", lambda b: uuid.UUID(bytes_le=b))
sqlite3.register_adapter(uuid.UUID, lambda u: u.bytes_le)

db = sqlite_utils.Database(DATABASE)
f = open("./share/stats_users.sql")
db.executescript(f.read())


# convert user_id to uuid
db["users"].convert("user_id", lambda value: fake.uuid4())


# copy games table
f = open("./share/stats_games.sql")
db.executescript(f.read())

# remove redundant int id from old users table
db["users"].transform(drop={"id"})
