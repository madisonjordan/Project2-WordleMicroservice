traefik: ./traefik --configFile=./etc/traefik.toml
word_validation: uvicorn --port $PORT --env-file="./api/words.env" --app-dir="./api" words:app --reload
answer_checking: uvicorn --port $PORT --env-file="./api/answers.env" --app-dir="./api" answers:app --reload
stats: uvicorn --port $PORT --env-file="./api/stats.env" --app-dir="./api"  stats:app --reload
