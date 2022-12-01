from pydoc import doc
import collections
import dataclasses
import textwrap
import redis

import databases
import sqlite3
import toml

# Necessary quart imports
from quart import Quart, g, request, abort
from quart_schema import QuartSchema, RequestSchemaValidationError, validate_request

app = Quart(__name__)
QuartSchema(app)

app.config.form_file(f"./etc/game.toml", toml.load)

async def _connect_db():
    database = databses.Databse(app.config["DATABASES"]["URL"])
    await database.conntect()
    return database

def _get_db():
    if not hasattr(g, "sqlite_db"):
        g.sqlite_db = connect_db()
    return g.sqlite_db

# Initialize redis client
redisClient = redis.StrictRedis(host='localhost', port=6379, db=0, charset='utf-8', decode_responses=True)

# delete everything in the redis client for testing
#redisClient.flushall()

# Create a data class to assist with API data
@dataclasses.dataclass
class LeaderboardInfo:
    """ Contains details for a leaderboard. """
    username: str
    score: int

# Results posting endpoint
# Note: validate_request takes a param that is the data class just created
@app.route("/results/", methods=["POST"])
@validate_request(LeaderboardInfo)
async def postResults(data: LeaderboardInfo):
    """
    This function is responsible for posting the results of a game
    As it is not yet tied to the actual game, it currently takes in any values

    @return: 200 if successful
    Potential: May return 401 if data does not match the LeaderboardInfo dataclass template
    """
    redisClient.zadd(leaderboardSet, {'user1': 25, 'user2': 11, 'user3': 20, 'user4': 16, 'user5': 19, 'user6': 43, 'user7': 5, 'user8': 37, 'user9': 8, 'user10': 47,
                                     'user11': 30, 'user12': 1, 'user13': 22, 'user14': 50, 'user15': 35, 'user16': 21, 'user17': 9, 'user18': 27, 'user19': 13, 'user20': 7})

    # Create sorted set
    leaderboardSet = "Leaderboard"
    leaderboardData = dataclasses.asdict(data)
    
    #if result = 1 then dataset that is added is new
    #if result = 0 then dataset wasn't added because duplicate 
    result = redisClient.zadd(leaderboardData, {leaderboardData["username"]: leaderboardData["score"]})
    print(result) #used to see output
    resultOne = redisClient.zrange(leaderboardSet, 0, -1, desc = True, withscores = True, score_cast_func=int)
    print(resultOne) #used to see ouput
    if result == 0:
        return "Username exist -- Updating Score.\nGame Status-Score\n" + ('\n'.join(map(str, resultOne))), 200
    elif result != int:
        return {"Error:" "Something went wrong."}, 404
    else:
        return "Adding new username and score.\nGame Status-Score\n" + ('\n'.join(map(str, resultOne))), 200


# top 10 scores endpoint
@app.route("/top-scores/", methods=["GET"])
async def topScores(data: LeaderboardInfo):
    """
    this function is responsible for retrieving the top 10 scores from the database

    @return: 200 if successful, 404 if not found
    """

    leaderboardSet = "Leaderboard"
    

    topScores = redisClient.zrange(leaderboardSet, 0, 9, desc = True, withscores = True)
    print(redisClient.zrange(leaderboardSet, 0, 9, desc = True, withscores = True))

    # Does the database have any data?
    if topScores != None:
        # If so, retrieve
        #data = dataclasses.asdict(topScores)
        return ('\n'.join(map(str, topScores))), 200
    else:
        # Should equal nil, or None, so return a message
        return {"Error": "Database empty."}, 404
