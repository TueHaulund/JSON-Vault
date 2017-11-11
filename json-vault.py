import flask
import tasks

app = flask.Flask(__name__)

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/api/v1.0/json', methods=['GET'])
def get_json():
    return flask.make_response(tasks.fetch(), 200, {'Content-Type': 'application/json'})

@app.route('/api/v1.0/json', methods=['POST'])
def post_json():
    json = flask.request.get_json()

    if not json:
        flask.abort(400)

    tasks.broadcast(json)
    tasks.store(json)
    return flask.make_response(flask.jsonify(json), 201)

if __name__ == '__main__':
    app.run(debug=True)