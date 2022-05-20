# Project 5 - Wordle Microservice

## Group Members

- Madison Jordan
- Jose Hernandez
- Ramon Amini
- Marco Andrade

## System Setup

OS: Tuffix (Ubuntu)

#### Install System Dependencies

```
  sudo apt update
  sudo apt install --yes python3-pip ruby-foreman sqlite3 httpie redis
```

#### Install Python Dependencies

```
  python3 -m pip install -r requirements.txt
```

## Execution Instructions

#### Initialize Databases:

1. run `./bin/init_db.sh` from project root directory

#### Start the Services:

1. `sudo service cron start` to start cron if it's not already running
2. run `./bin/init.sh` from project root directory
3. `foreman start`

#### Testing the Services:

1. You can run tests from the autodocs interface

_Note: The answer check function and new game creation uses `gameid`, which is implemented as the current date (in UTC timezone by default). Games will be played based on the UTC date and therefore might not match the date in your timezone._

See changes to past services in `CHANGELOG.md`