import psycopg2
import itertools
import os
import sys

try:
    params = {
        'dbname': 'json-vault',
        'host': 'localhost',
        'user': os.environ['PSQL_USER'],
        'password': os.environ['PSQL_PW']
    }

    conn = psycopg2.connect(**params)
except:
    print("Could not connect to PostgreSQL")
    sys.exit()

def store(json):
    print('Storing: %s' % json)
    cur = conn.cursor()
    cur.execute('INSERT INTO json(data) VALUES (%s)', (json,))
    cur.close()
    conn.commit()

def fetch():
    print('Fetching')
    cur = conn.cursor()
    cur.execute('SELECT * FROM json')
    raw_data = cur.fetchall()
    cur.close()
    return list(itertools.chain(*raw_data)) #Collapse list of tuples to plain list

def broadcast(json):
    print('Broadcasting: %s' % json)
    #TODO: Broadcast over WebSockets