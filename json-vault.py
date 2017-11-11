import flask
import tasks

app = flask.Flask(__name__)

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/api/v1.0/json', methods=['GET'])
def get_json():
    return flask.jsonify(tasks.fetch())

@app.route('/api/v1.0/json', methods=['POST'])
def post_json():
    if not flask.request.is_json:
        flask.abort(400)

    #We should check payload length before doing this
    json_string = flask.request.get_data().decode("utf-8")

    tasks.broadcast(json_string)
    tasks.store(json_string)
    return flask.make_response(json_string, 201)

if __name__ == '__main__':
    app.run(debug=True)