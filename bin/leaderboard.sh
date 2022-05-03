. ~/.bash_profile && \
echo "Update Leaderboard: $(date)" && \
$PROJ_PATH/dist/getTop10 | redis-cli --pipe 