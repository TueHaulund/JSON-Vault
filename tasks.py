import celery
import psycopg2
import itertools
import os
from _celery import celery_app

db_params = {
    'dbname': 'jsonvault',
    'host': 'localhost',
    'user': os.environ['PSQL_USER'],
    'password': os.environ['PSQL_PW']
}

class DatabaseTask(celery.Task):
    _db = None

    @property
    def db(self):
        if self._db is None:
            self._db = psycopg2.connect(**db_params)
        return self._db

@celery_app.task(base = DatabaseTask, ignore_result = True)
def store(json):
    cur = store.db.cursor()
    cur.execute('INSERT INTO json(data) VALUES (%s)', (json,))
    cur.close()
    store.db.commit()

@celery_app.task(base = DatabaseTask)
def fetch():
    cur = fetch.db.cursor()
    cur.execute('SELECT * FROM json')
    raw_data = cur.fetchall()
    cur.close()
    return list(itertools.chain(*raw_data)) #Collapse list of tuples to plain list

@celery_app.task(ignore_result = True)
def broadcast(json):
    print('Broadcasting: %s' % json)
    #TODO: Broadcast over WebSockets