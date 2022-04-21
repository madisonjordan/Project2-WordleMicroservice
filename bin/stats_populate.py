import sqlite3
import uuid
from faker import Faker
from faker.factory import Factory
import sqlite_utils
import datetime
from datetime import date, timedelta

# use UUID in table
sqlite3.register_converter("GUID", lambda b: uuid.UUID(bytes_le=b))
sqlite3.register_adapter(uuid.UUID, lambda u: u.bytes_le)

# use faker to create fake user and game data
Faker = Factory.create
fake = Faker()
fake.seed(0)

num_users = 1000

fake_users = [
    {
        "user_id": str(uuid.uuid4()),
        "username": fake.user_name(),
    }
    for x in range(num_users)
]

# add fake users to users table
db = sqlite_utils.Database("./var/stats.db")
db["users"].insert_all(fake_users)


# faker date_between() etc functions not working
start_date = datetime.date(2022, 1, 1)
end_date = datetime.date.today()
day_range = (end_date - start_date).days

# generate games for a user
games = [0] * num_users

# all fake games
num_games = 10000
fake_games = []

for i in range(num_games):
    curr_user = fake.random_int(min=0, max=num_users - 1)
    games[curr_user] += 1
    user_id = fake_users[curr_user].get("user_id")
    game_id = games[curr_user]
    game = {
        "user_id": user_id,
        "game_id": game_id,
        "finished": (
            start_date + datetime.timedelta(days=fake.random_int(min=0, max=day_range))
        ),
        "guesses": fake.random_int(min=1, max=6),
        "won": fake.boolean(chance_of_getting_true=75),
    }
    fake_games.append(game)

# add fake games to games table
db = sqlite_utils.Database("./var/stats.db")
db["games"].insert_all(fake_games)
