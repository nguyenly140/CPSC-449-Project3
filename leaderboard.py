from pydoc import doc
import collections
import dataclasses
import textwrap
import redis

import json

# Necessary quart imports
from quart import Quart, g, request, abort
from quart_schema import QuartSchema, RequestSchemaValidationError, validate_request

app = Quart(__name__)
QuartSchema(app)

# Initialize redis client
redisClient = redis.Redis(host='localhost', port=6379, db=0)

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

    # adding data to redis-server


    # Create sorted set
    leaderboardSet = "Leaderboard"
    leaderboardData = dataclasses.asdict(data)

    # Were we able to post?
    #if redisClient.zadd(leaderboardSet, leaderboardData[score], leaderboardData[username]) == 1:
    #    return leaderboardData, 200
    #else:
    #    return {"Error:" "Something went wrong."}, 404
    #if result = 1 then dataset that is added is new
    #if result = 0 then dataset wasn't added because duplicate 
    result = redisClient.zadd(leaderboardSet, {leaderboardData["username"]: leaderboardData["score"]})
    print(result)
    resultOne = redisClient.zrange(leaderboardSet, 0, -1, desc = True, withscores = True)
    print(type(resultOne))
    print(resultOne)
    if result == 0:
        #print(resultOne)
        #return {"username exist: updating score.": leaderboardData}, 200
        return str(resultOne)
    #else:
        #print(resultOne)
        #return {"Adding new username and score.": leaderboardData}, 200


# top 10 scores endpoint
@app.route("/top-scores/", methods=["GET"])
async def topScores():
    """
    this function is responsible for retrieving the top 10 scores from the database

    @return: 200 if successful, 404 if not found
    """

    leaderboardSet = "Leaderboard"
    
    redisClient.zadd(leaderboardSet, {'user1': 25, 'user2': 11, 'user3': 20, 'user4': 16, 'user5': 19, 'user6': 43, 'user7': 5, 'user8': 37, 'user9': 8, 'user10': 47,
                                     'user11': 30, 'user12': 1, 'user13': 22, 'user14': 50, 'user15': 35, 'user16': 21, 'user17': 9, 'user18': 27, 'user19': 13, 'user20': 7})

    topScores = redisClient.zrange(leaderboardSet, 0, 9, desc = True, withscores = True)
    print(redisClient.zrange(leaderboardSet, 0, 9, desc = True, withscores = True))

    # Does the database have any data?
    if topScores != "":
        # If so, retrieve
        #data = dataclasses.asdict(topScores)
        return topScores, 200
    else:
        # Should equal nil, or None, so return a message
        return {"Error": "Database empty."}, 404
