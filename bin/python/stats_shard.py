import contextlib
import datetime
import random
import sqlite3
import sqlite_utils
import uuid
import collections

import faker

NUM_STATS = 1_000_000
NUM_USERS = 100_000
YEAR = 2022

shards = 3

random.seed(YEAR)
fake = faker.Faker()
fake.seed(YEAR)

sqlite3.register_converter("GUID", lambda b: uuid.UUID(bytes_le=b))
sqlite3.register_adapter(uuid.UUID, lambda u: u.bytes_le)


def getShardId(string_uuid):
    curr_uuid = uuid.UUID(string_uuid)
    return curr_uuid.int % shards


DATABASE = "./var/stats_full.db"

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


shard_users = collections.defaultdict(list)
shard_games = collections.defaultdict(list)

for row in db["users"].rows:
    user_id = row.get("user_id")
    shard_id = getShardId(user_id)
    shard_users[shard_id].append(row)

for row in db["games"].rows:
    user_id = row.get("user_id")
    shard_id = getShardId(user_id)
    shard_games[shard_id].append(row)


# shard users database

stats_db = ["./var/stats0.db", "./var/stats1.db", "./var/stats2.db"]

for i in range(shards):
    db = sqlite_utils.Database(stats_db[i])
    db["users"].insert_all(shard_users[i])
    print(f"shard {i} - users created")
    db["games"].insert_all(shard_games[i])
    print(f"shard {i} - game stats created")
