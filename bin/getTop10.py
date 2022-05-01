import sqlite3
import uuid
import collections
import itertools

shards = 3
database_dir = "./var/"


def top10_streaks_all_time():
    shard_top10 = collections.defaultdict(list)
    temp = []
    all_list = []
    top10 = []
    for shard in range(shards):
        db = sqlite3.connect(f"{database_dir}stats{shard}.db")
        shard_top10[shard] = db.execute(
            "SELECT streaks.user_id, users.username, streaks.streak FROM streaks INNER JOIN users ON streaks.user_id=users.user_id ORDER BY streak DESC LIMIT 10"
        ).fetchall()
        temp.append(shard_top10[shard])
    all_list = list(itertools.chain(*temp))
    for user in range(10):
        user_streak = {
            "user_id": all_list[user][0],
            "username": all_list[user][1],
            "streak": all_list[user][2],
        }
        top10.append(user_streak)
    return top10


print(top10_streaks_all_time())
