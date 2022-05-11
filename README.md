# Project 4 - Wordle Microservice

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
