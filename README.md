# JSONVault

Simple app for storing and fetching arbitrary JSON.

Altogether the app consists of:
  - Flask-based web application
  - Celery task queue
  - Redis instance, used as both broker and result-backend for Celery
  - PostgreSQL instance, used as the storage backend

# API

The application provides a single endpoint at '/api/v1.0/json' supporting the methods:

**POST** - stores any given JSON object in the database and also broadcasts this object over WebSockets

**GET** - returns a JSON array containing all objects stored so far

Additionally, the app will return a simple HTML page on '/', implementing a *client* which can be used to connect to the server with WebSockets.

Using cURL, we can interact with a running instance of JSONVault with these commands:

`curl -i -X POST -d '{"example": "json"}' -H 'Content-Type: application/json' http://localhost:5000/api/v1.0/json`

`curl -i -X GET http://localhost:5000/api/v1.0/json`

# Deployment

The repo contains a docker-compose setup which launches 4 containers running the web application, the Celery workers, the Redis instance and a PostgreSQL instance. The database is persisted to ./data/postgres, the Redis instance is not persisted at all. By default, the application listens on port 5000 and this port is also mapped to 5000 by Docker.

Launching the app:
1. Run `docker-compose build`
2. Run `docker-compose up`
3. Visit http://localhost:5000 to use the WebSockets client
4. Use the cURL commands listed above to interact with the REST API

**NOTE**: For simplicity's sake, the docker-compose YAML file contains the database credentials used by the application. Which also means they're included by Git and hosted here on GitHub. Obviously don't do this for an actual production application.

# Testing

The repository contains a few unit tests which can be run from the root of the repo with:

`python3 -m unittest discover test`

When testing the Flask application (./test/test_jsonvault.py) we use a mock of the Celery tasks to keep the tests self-contained and avoid the need for a proper backend. When testing the Celery tasks (./test/test_jsonvault_tasks.py) we use a mock of the DB connector for the same reasons.

**TESTING ROADMAP:**
- Implement integration or end-to-end tests, possibly using *WebTest*
- Replace standard *unittest* module with *pytest* or *Nose*

# Development

The Flask application is defined in *jsonvault.py* and the Celery tasks (*store* and *fetch*) are defined in *jsonvault_tasks.py*.

The JSON objects are stored directly as plain strings in the database. For a more realistic/complex application we should instead use an ORM, such as SQLAlchemy. This decouples the application from the choice of database and automates the mapping between SQL relations and in-memory representations of the model.

The *store*-task runs asynchronously while the Flask app blocks when running the *fetch*-task as it needs the results in order to issue a reply. The *fetch* task could be made asynchronous by instead returning a task ID which the client could then poll on another endpoint until the results are ready. This moves the heavy-lifting outside of the request/response cycle which frees up resources for dealing with other requests while the DB is working.

The WebSockets client is served from ./static/index.html and is implemented in JS and HTML with the SocketIO library. A fallback is automatically used if WebSockets are not available. I resisted the urge not to put a fabulous scrolling marquee on the page... but only because MDN says &lt;marquee&gt; is deprecated!
