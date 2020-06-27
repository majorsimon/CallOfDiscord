#!python3
from apscheduler.schedulers.blocking import BlockingScheduler
from pymongo import MongoClient
from datetime import datetime
import logging
import urllib
import cod
import os


# Create a custom logger
logger = logging.getLogger(__name__)

# Create handler
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
# Create formatter and add it to handler
lformat = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(lformat)
# Add handler to the logger
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

def error_exit(message):
    logger.error(message)
    os.sys.exit(1)

def getDBClient(
    username: urllib.parse.quote_plus, 
    password: urllib.parse.quote_plus, 
    database,
    host='mongodb', 
    port=27017
    ):

    connstr = "mongodb://%s:%s@%s:%s" % (username, password, host, port)
    return MongoClient(connstr)[database]

def getUsers(mongo):
    return [user for user in mongo['codusers'].find()]

def getCodClient(user):
    client = cod.CallOfDutyAPIClient(platform=user['cod-api']['platform'])
    client.cookies = user['cod-api']['cookies']
    client.headers = user['cod-api']['headers']
    client.loggedIn = True
    return client

def getLatestStats(user):
    logger.info("Fetching stats for user '%s'..." % user['nicename'])

    logger.debug('Creating CoD-API client for user...')
    client = getCodClient(user)
    logger.debug('Finished creating CoD-API client for user')

    results = {}
    for name, endpoint in cod.COD_ENDPOINTS['user'].items():
        title = 'mw'
        platform = user['cod-api']['platform']
        startdate = 0
        enddate = 0
        userid = user['cod-api']['userid']

        logger.debug("Fetching '%s' stats..." % name)
        results[name] = client.sendRequest(
            cod.DEFAULT_BASE_URL, 
            endpoint.format(locals()),
            'GET'
        )
        logger.debug("Finished fetching '%s' stats" % name)

    logger.info("Finished fetching stats for user '%s'" % user['nicename'])
    return results

def addLatestStats(mongo, stats):
    mongo['codstats'].insert_many(stats)

def doTheThing():
    logger.info('Running stats collection')
    creds = {
        'username': os.environ.get('MONGO_READWRITE_USER'),
        'password': os.environ.get('MONGO_READWRITE_PASS'),
        'database': os.environ.get('MONGO_DB_NAME')
    }
    cantproceed = False
    for k, v in creds.items():
        if v is None or len(v.strip()) == 0:
            logger.error("No value for %s!" % k)
            cantproceed = True
    if cantproceed is True:
        error_exit('Missing mongodb configuration')

    logger.info('MongoDB credentials defined')
    mongo = getDBClient(creds['username'], creds['password'], creds['database'])
    logger.info('MongoDB client defined')

    logger.info('Fetching users...')
    users = getUsers(mongo)
    logger.info('Finished fetching users')

    logger.info('Fetching stats...')
    stats = [getLatestStats(user) for user in users]
    logger.info('Finished fetching stats')

    logger.info('Pushing stats to DB...')
    addLatestStats(mongo, stats)
    logger.info('Finished pushing stats to DB')

    logger.info('Finished running stats collection')

def main():
    logger.info('Starting...')
    scheduler = BlockingScheduler()
    scheduler.add_job(doTheThing, 'interval', minutes=1, start_date=datetime(2000, 1, 1, 0, 0, 0))
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass
    logger.info('Bye-bye')
    os.sys.exit()

main()

