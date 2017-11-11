import flask
import json
import tasks

MAX_PAYLOAD_SIZE = 1024 * 1024 #One MiB

flask_app = flask.Flask(__name__)

def is_valid_json(json_string):
    try:
        json_dict = json.loads(json_string)
    except ValueError as e: #EAFP
        return False
    return True

@flask_app.route('/')
def index():
    return flask_app.send_static_file('index.html')

@flask_app.route('/api/v1.0/json', methods=['GET'])
def get_json():
    async_result = tasks.fetch.delay()
    result = async_result.wait(timeout = None)
    return flask.make_response('[' + ','.join(result) + ']', 200)

@flask_app.route('/api/v1.0/json', methods=['POST'])
def post_json():
    if not flask.request.is_json:
        flask.abort(400)

    if not flask.request.content_length:
        flask.abort(411)

    if flask.request.content_length > MAX_PAYLOAD_SIZE:
        flask.abort(413)

    json_string = flask.request.get_data().decode("utf-8")

    if not is_valid_json(json_string):
        flask.abort(400)

    tasks.broadcast.delay(json_string)
    tasks.store.delay(json_string)
    return flask.make_response(json_string, 201)

if __name__ == '__main__':
    flask_app.run(debug=True)