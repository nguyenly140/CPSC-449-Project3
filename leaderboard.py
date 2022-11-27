from pydoc import doc
import databases
import collections
import dataclasses
import sqlite3
import textwrap
import uuid
import redis
import toml

# The statistics library has been a standard python library since v3.4, so may be used
from statistics import mean
from quart import Quart, g, request, abort
from quart_schema import QuartSchema, RequestSchemaValidationError, validate_request

app = Quart(__name__)
QuartSchema(app)

# Just in case, load the game database config file
app.config.from_file(f"./etc/game.toml", toml.load)


# Initialize a connection to the redis database
rdb = redis.Redis(host='localhost', port=6379, db=0)

async def _connect_db():
    database = databases.Database(app.config["DATABASES"]["URL"])
    await database.connect()
    return database

async def _connect_replica_db():
    random_db = random.randint(0, 2)

    if(random_db == 0):
        database = databases.Database(app.config["DATABASES"]["URL"])
    elif(random_db == 1):
        database = databases.Database(app.config["DATABASES"]["URLONE"])
    else:
        database = databases.Database(app.config["DATABASES"]["URLTWO"])

    app.logger.info(random_db)
    await database.connect()
    return database

def _get_db():
    if not hasattr(g, "sqlite_db"):
        g.sqlite_db = _connect_db()
    return g.sqlite_db

def _get_replica_db():
    if not hasattr(g, "sqlite_replica_db"):
        g.sqlite_replica_db = _connect_replica_db()
    return g.sqlite_replica_db


# Results posting endpoint
@app.route("/results/<string:status>/<int:guesses>", methods=["POST"])
async def postResults(status, guesses):
    """
    This function is responsible for posting the results of a game
    As it is not yet tied to the actual game, it currently takes in any values

    @status: The status of a game, either won or lost
    @guesses: The number of guesses it took

    @return: 200 for success
    """

    # Create keys
    rdbKeyValPairs = {"status": status, "guesses": guesses}

    # Now set the data
    rdb.mset(rdbKeyValPairs)

    return 200


@app.route("/top-scores/", methods=["GET"])
async def topScores():
    """
    this function is responsible for displaying the top 10 scores found in the database
    """

    results = []
    db = await _get_db()

    # Get the guesses and convert to scores
    select_query = "SELECT guesses FROM guess"
    values = {"guesses": "guesses"}

    results = db.fetch_all(select_query, values)
    average = mean(results)

    return average, 200
