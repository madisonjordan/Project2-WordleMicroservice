import sqlite3
import uuid
from faker import Faker
from faker.providers import BaseProvider
from faker.factory import Factory
import sqlite_utils
import datetime
from datetime import date, timedelta
import collections

# use UUID in table
sqlite3.register_converter("GUID", lambda b: uuid.UUID(bytes_le=b))
sqlite3.register_adapter(uuid.UUID, lambda u: u.bytes_le)
# str(uuid.uuid4()),

# create fake user data
Faker = Factory.create
NUM_STATS = 1_000_000
NUM_USERS = 100_000
YEAR = 2022

fake = Faker()
fake.seed(YEAR)

# create unique usernames and uuids
usernames_unique = set()

while len(usernames_unique) in range(NUM_USERS):
    user = fake.user_name()
    usernames_unique.add(user)

usernames = list(usernames_unique)

fake_users = [
    {"user_id": fake.uuid4(), "username": usernames[x]} for x in range(NUM_USERS)
]


# create shards for games stats databases
shards = 3
shard_users = collections.defaultdict(list)
shard_games = collections.defaultdict(list)


def getShardId(string_uuid):
    curr_uuid = uuid.UUID(string_uuid)
    return curr_uuid.int % shards


# generate games until today
end_date = datetime.date.today()


for i in range(NUM_USERS):
    user_id = fake_users[i].get("user_id")
    # insert user into proper shard
    shard_id = getShardId(user_id)
    shard_users[shard_id].append(fake_users[i])
    # generate games for this user
    games_played = fake.random_int(min=1, max=100)
    # fake first game date for each user
    game_id = 0
    user_date = end_date - datetime.timedelta(days=games_played)
    # games played by this user (plays every day) until today
    for i in range(games_played):
        # increment date and game for this user
        game_id += 1
        user_date += datetime.timedelta(days=1)
        # game data
        game = {
            "user_id": user_id,
            "game_id": game_id,
            "finished": user_date,
            "guesses": fake.random_int(min=1, max=6),
            "won": fake.boolean(chance_of_getting_true=75),
        }
        # enter user's game into the correct shard
        shard_games[shard_id].append(game)


# add fake games to games table
stats_db = ["./var/stats0.db", "./var/stats1.db", "./var/stats2.db"]

for i in range(shards):
    db = sqlite_utils.Database(stats_db[i])
    db["users"].insert_all(shard_users[i])
    db["games"].insert_all(shard_games[i])
