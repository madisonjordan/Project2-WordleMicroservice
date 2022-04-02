import sqlite3

# connect to words database (pre-created) in read-only
con = sqlite3.connect('file:database/words.db?mode=ro')
cur = con.cursor()

# get all words in database
words = con.execute("""
    select * from words
""").fetchall()

# user guess
guess="shinist"

# find guess in word list
guess_is_valid = con.execute(f"""
    select * from words where word='{guess}'
    """
).fetchone()

if(guess_is_valid is None):
    print(f"'{guess}' is not a valid guess")
else:
    print(guess)

# close connection to database
con.close()