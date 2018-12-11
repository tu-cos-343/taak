"""
Configuration for API server.

This configuration is used both by the server and the tests.

To run the code here, you'll need to provide credentials for both a Mongo
instance (e.g., at mlab.com) and PostgreSQL (e.g., on Faraday).

We never want to end up with credentials in Git, so a common practice
is to store them in environment variables. Here's an easy way to do so:

- Define a file called (say) 'private-env.sh' containing envioronment variables
  that configure your database connections.
- In the bash shell where you run the server (or tests)
     source private-env.sh
  just like you do to start up a virtual envionrment.

Here's a template for 'private-env.sh':

# --------------------------------
# MongoDB at mlab
export MLAB_USER='<mlab user id>'
export MLAB_PASS='<mlab password>'
export MLAB_URL='ds151463.mlab.com:51463'
export MLAB_DB='cos-343-f18'

# Postgres
export PSQL_HOST='faraday.cse.taylor.edu'
export PSQL_DB='taak'
export PSQL_USER='<psql user id>'
export PSQL_PASSWORD='<psql password>'
--------------------------------

"""
import os

import psycopg2.extras
from pymongo import MongoClient

# Mongo
mlab_user = os.environ['MLAB_USER']
mlab_pass = os.environ['MLAB_PASS']
mlab_url = os.environ['MLAB_URL']
mlab_db = os.environ['MLAB_DB']

# Postgres
psql_host = os.environ['PSQL_HOST']
psql_dbname = os.environ['PSQL_DB']
psql_user = os.environ['PSQL_USER']
psql_password = os.environ['PSQL_PASSWORD']

mongo_uri = 'mongodb://{}:{}@{}/{}'.format(mlab_user, mlab_pass, mlab_url, mlab_db)
mongo_client = MongoClient(mongo_uri)
mongo_db = mongo_client[mlab_db]

psql_db = psycopg2.connect(host=psql_host,
                           dbname=psql_dbname,
                           user=psql_user,
                           password=psql_password,
                           cursor_factory=psycopg2.extras.RealDictCursor)
