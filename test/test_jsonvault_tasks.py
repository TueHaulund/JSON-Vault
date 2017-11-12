from unittest import TestCase, mock

import jsonvault_tasks

class TestStore(TestCase):
    @mock.patch('jsonvault_tasks.psycopg2.connect')
    @mock.patch('jsonvault_tasks.store.conn', new = None) #Clear DB connection so task will attempt to create a new one
    @mock.patch.dict('jsonvault_tasks.os.environ', clear = True) #Clear environment variables
    def test_store_missing_credentials(self, mock_connect):
        #Test that store raises a runtime error when DB credentials are missing
        self.assertRaises(RuntimeError, jsonvault_tasks.store, 'dummy')
    
    @mock.patch('jsonvault_tasks.psycopg2.connect')
    @mock.patch('jsonvault_tasks.store.conn', new = None) #Clear DB connection so task will attempt to create a new one
    @mock.patch.dict('jsonvault_tasks.os.environ', {'PSQL_USER': 'dummyuser', 'PSQL_PW': 'dummypw'}) #Provide dummy DB credentials
    def test_store_invoked_connect(self, mock_connect):
        #Test that connect() is called with the right arguments when DB credentials are in place
        jsonvault_tasks.store('dummy')
        mock_connect.assert_called_with(dbname='jsonvault', host='localhost', password='dummypw', user='dummyuser')

    @mock.patch('jsonvault_tasks.psycopg2.connect')
    @mock.patch('jsonvault_tasks.store.conn', new = None)
    def test_store_invoked(self, mock_connect):
        #Test that store invokes the right DB methods
        jsonvault_tasks.store('dummy')
        self.assertTrue(mock_connect.called)
        self.assertTrue(mock_connect().cursor.called)
        self.assertTrue(mock_connect().cursor().execute.called)
        self.assertTrue(mock_connect().cursor().close.called)
        self.assertTrue(mock_connect().commit.called)

    @mock.patch('jsonvault_tasks.psycopg2.connect')
    @mock.patch('jsonvault_tasks.store.conn', new = None)
    def test_store_invoked_with(self, mock_connect):
        #Test that store executes an SQL statement with the provided JSON string
        jsonvault_tasks.store('{"example": "json"}')
        execute_calls = mock_connect().cursor().execute.call_args_list
        self.assertEqual(len(execute_calls), 1)
        self.assertTrue('{"example": "json"}' in str(execute_calls[0]))

class TestFetch(TestCase):
    @mock.patch('jsonvault_tasks.psycopg2.connect')
    @mock.patch('jsonvault_tasks.fetch.conn', new = None) #Clear DB connection so task will attempt to create a new one
    @mock.patch.dict('jsonvault_tasks.os.environ', clear = True) #Clear environment variables
    def test_fetch_missing_credentials(self, mock_connect):
        #Test that fetch raises a runtime error when DB credentials are missing
        self.assertRaises(RuntimeError, jsonvault_tasks.fetch)
    
    @mock.patch('jsonvault_tasks.psycopg2.connect')
    @mock.patch('jsonvault_tasks.fetch.conn', new = None) #Clear DB connection so task will attempt to create a new one
    @mock.patch.dict('jsonvault_tasks.os.environ', {'PSQL_USER': 'dummyuser', 'PSQL_PW': 'dummypw'}) #Provide dummy DB credentials
    def test_fetch_invoked_connect(self, mock_connect):
        #Test that connect() is called with the right arguments when DB credentials are in place
        jsonvault_tasks.fetch()
        mock_connect.assert_called_with(dbname='jsonvault', host='localhost', password='dummypw', user='dummyuser')

    @mock.patch('jsonvault_tasks.psycopg2.connect')
    @mock.patch('jsonvault_tasks.fetch.conn', new = None)
    def test_fetch_invoked(self, mock_connect):
        #Test that fetch invokes the right DB methods
        jsonvault_tasks.fetch()
        self.assertTrue(mock_connect.called)
        self.assertTrue(mock_connect().cursor.called)
        self.assertTrue(mock_connect().cursor().execute.called)
        self.assertTrue(mock_connect().cursor().fetchall.called)
        self.assertTrue(mock_connect().cursor().close.called)

    @mock.patch('jsonvault_tasks.psycopg2.connect')
    @mock.patch('jsonvault_tasks.fetch.conn', new = None)
    def test_fetch_return(self, mock_connect):
        #Test that fetch returns the JSON string provided by the DB
        mock_connect().cursor().fetchall.return_value = [('{"example": "json"}',), ('{"more": "json"}',)]
        self.assertEqual(jsonvault_tasks.fetch(), ['{"example": "json"}', '{"more": "json"}'])

