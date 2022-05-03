# Top10 leaderboard script to be built as a standalone using pyinstaller
# pyinstaller --onefile getTop10.py
import os
import sqlite3
import collections
import itertools

shards = 3
database_dir = os.environ["PROJ_PATH"] + "/var/"

# print Streaks - Top10 from each shard
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
    for user in range(30):
        print("zadd", "streaks", all_list[user][2], '"' + all_list[user][1] + '"')


# print Wins - Top10 from each shard
def top10_wins():
    shard_top10 = collections.defaultdict(list)
    temp = []
    all_list = []
    top10 = []
    for shard in range(shards):
        db = sqlite3.connect(f"{database_dir}stats{shard}.db")
        shard_top10[shard] = db.execute(
            "SELECT wins.user_id, users.username, wins.wins FROM wins INNER JOIN users ON wins.user_id=users.user_id ORDER BY wins DESC LIMIT 10"
        ).fetchall()
        temp.append(shard_top10[shard])
    all_list = list(itertools.chain(*temp))
    for user in range(30):
        print("zadd", "wins", all_list[user][2], '"' + all_list[user][1] + '"')


# output for redis
top10_streaks_all_time()
top10_wins()
