import sqlite3
import uuid
from faker import Faker
import sqlite_utils

sqlite3.register_converter("GUID", lambda b: uuid.UUID(bytes_le=b))
sqlite3.register_adapter(uuid.UUID, lambda u: u.bytes_le)

fake = Faker()
fake.seed(0)

num_users = 10000

fake_users = [
    {
        "user_id": str(uuid.uuid4()),
        "username": fake.user_name(),
    }
    for x in range(num_users)
]

db = sqlite_utils.Database("./var/stats.db")
db["users"].insert_all(fake_users)
