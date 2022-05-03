traefik: ./traefik --configFile=./etc/traefik.toml
word_validation: touch var/log/api.log && uvicorn --port $PORT words:app --reload
answer_checking: uvicorn --port $PORT answers:app --reload
stats: uvicorn --port $PORT stats:app --reload
redis: redis-server
