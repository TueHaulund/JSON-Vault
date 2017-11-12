from unittest import TestCase, mock

import jsonvault

class TestJSONVault(TestCase):
    def setUp(self):
        self.flask_app = jsonvault.flask_app.test_client()
        self.flask_app.testing = True

    def test_is_valid_json(self):
        self.assertTrue(jsonvault.is_valid_json('{"example": "json"}'))
        self.assertTrue(jsonvault.is_valid_json('[{"example": "json"},{"more": "json"}]'))
        self.assertFalse(jsonvault.is_valid_json('notjson'))
        self.assertFalse(jsonvault.is_valid_json(''))

    @mock.patch('jsonvault.tasks.fetch')
    def test_get_json_invoked(self, mock_fetch):
        #Test that fetch task is invoked
        self.flask_app.get('/api/v1.0/json')
        self.assertTrue(mock_fetch.delay.called)
        self.assertTrue(mock_fetch.delay().wait.called)
    
    @mock.patch('jsonvault.tasks.fetch')
    def test_get_json_return(self, mock_fetch):
        #Test result of valid GET request
        mock_fetch.delay().wait.return_value = ['{"example": "json"}', '{"more": "json"}']
        resp = self.flask_app.get('/api/v1.0/json')
        self.assertEqual(resp.get_data().decode('utf-8'), '[{"example": "json"},{"more": "json"}]')

    @mock.patch('jsonvault.tasks.store')
    @mock.patch('jsonvault.socketio_app')
    def test_post_json_invoked(self, mock_socketio, mock_store):
        #Test that store task and socket.emit is invoked
        resp = self.flask_app.post('/api/v1.0/json', data = '{"example": "json"}', content_type = "application/json")
        self.assertTrue(mock_store.delay.called)
        self.assertTrue(mock_socketio.emit.called)

    @mock.patch('jsonvault.tasks.store')
    @mock.patch('jsonvault.socketio_app')
    def test_post_json_return(self, mock_socketio, mock_store):
        #Test valid POST request
        resp = self.flask_app.post('/api/v1.0/json', data = '{"example": "json"}', content_type = "application/json")
        self.assertEqual(resp.status, "201 CREATED")
        self.assertEqual(resp.get_data().decode('utf-8'), '{"example": "json"}')
        mock_socketio.emit.assert_called_with('json', '{"example": "json"}')
        mock_socketio.emit.reset_mock()

        #Test missing Content-Type header
        resp = self.flask_app.post('/api/v1.0/json', data = '{"example": "json"}')
        self.assertEqual(resp.status, "400 BAD REQUEST")
        mock_socketio.emit.assert_not_called()

        #Test invalid JSON POST
        resp = self.flask_app.post('/api/v1.0/json', data = '{"example": "json"]', content_type = "application/json")
        self.assertEqual(resp.status, "400 BAD REQUEST")
        mock_socketio.emit.assert_not_called()

        #Request too large
        large_json = '{"example": "' + (jsonvault.MAX_PAYLOAD_SIZE * 'json') + '"}'
        resp = self.flask_app.post('/api/v1.0/json', data = large_json, content_type = "application/json")
        self.assertEqual(resp.status, "413 REQUEST ENTITY TOO LARGE")
        mock_socketio.emit.assert_not_called()

    #Something in Flask is causing Python to emit a ResourceWarning when running this test
    #It appears to be harmless and it only happens when testing
    def test_get_index(self):
        #Test that the index.html file is returned on '/'
        resp = self.flask_app.get('/')
        index_html = resp.get_data().decode('utf-8')
        with open('static/index.html') as index_file:
            self.assertEqual(index_file.read(), index_html)