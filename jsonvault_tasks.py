import celery
import psycopg2
import itertools
import os
import sys

from _celery import celery_app

class DatabaseTask(celery.Task):
    conn = None

    @property
    def db(self):
        if self.conn is None:
            try:
                db_params = {
                    'dbname': 'jsonvault',
                    'host': 'localhost',
                    'user': os.environ['PSQL_USER'],
                    'password': os.environ['PSQL_PW']
                }
            except:
                raise RuntimeError("No database credentials provided")
            
            self.conn = psycopg2.connect(**db_params)
        return self.conn

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