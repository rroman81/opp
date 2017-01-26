from datetime import timedelta
import json
import logging

from flask import escape, Flask, redirect, request, session, url_for

from opp.api.v1 import categories, items, users
from opp.common import opp_config, utils
from opp.db import api
from opp.flask.flask_jwt import JWT, jwt_required


CONF = opp_config.OppConfig()

# Logging config
logname = CONF['log_filename'] or '/tmp/openpassphrase.log'
logging.basicConfig(filename=logname, level=logging.DEBUG)


# JWT and session configs
if CONF['secret_key'] == "default-insecure":
    logging.warning("Config option 'secret_key' not specified."
                    " Using default insecure value!")
try:
    exp_delta = int(CONF['exp_delta'])
    if CONF['exp_delta'] > pow(2, 31):
        logging.warning("Invalid value specified for 'exp_delta' "
                        "config option. Defaulting to 300 seconds.")
        exp_delta = 300
except Exception:
    logging.warning("Invalid value specified for 'exp_delta' "
                    "config option. Defaulting to 300 seconds.")
    exp_delta = 300

# Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = CONF['SECRET_KEY']
app.config['EXP_DELTA'] = timedelta(seconds=exp_delta)
app.config['PREFERRED_URL_SCHEME'] = "https"

if __name__ == "__main__":
    app.run()


def authenticate(username, password):
    user = api.user_get_by_username(username)
    if user and utils.checkpw(password, user.password):
        return user
    return None


def identity(payload):
    return api.user_get_by_id(payload['identity'])


jwt = JWT(app, authenticate, identity)


def _to_json(dictionary):
    return json.dumps(dictionary)


def _enforce_content_type():
    try:
        content_type = request.headers['Content-Type']
    except KeyError:
        return '{"error": "Mising Content-Type"}'
    if content_type != "application/json":
        return '{"error": "Invalid Content-Type"}'


@app.route("/api/v1/health")
def health_check():
    return _to_json({'status': "OpenPassPhrase service is running"})


@app.route("/users", methods=['PUT', 'POST', 'DELETE'])
def handle_users():
    err = _enforce_content_type()
    if err:
        return err, 400
    handler = users.ResponseHandler(request)
    response = handler.respond(require_phrase=False)
    return _to_json(response)


@app.route("/api/v1/categories",
           methods=['GET', 'PUT', 'POST', 'DELETE'])
@jwt_required()
def handle_categories():
    err = _enforce_content_type()
    if err:
        return err, 400
    handler = categories.ResponseHandler(request)
    # Set require_phrase to True for all methods except DELETE
    response = handler.respond(request.method != 'DELETE')
    return _to_json(response)


@app.route("/api/v1/items",
           methods=['GET', 'PUT', 'POST', 'DELETE'])
@jwt_required()
def handle_items():
    err = _enforce_content_type()
    if err:
        return err, 400
    handler = items.ResponseHandler(request)
    # Set require_phrase to True for all methods except DELETE
    response = handler.respond(request.method != 'DELETE')
    return _to_json(response)


@app.route('/')
def index():
    if 'username' in session:
        return 'Logged in as %s' % escape(session['username'])
    return 'You are not logged in'


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if authenticate(request.form['username'], request.form['password']):
            session['username'] = request.form['username']
            return redirect(url_for('index'))
        else:
            return redirect(url_for('login'))
    return '''
        <form method="post">
            <p>username: <input type=text name=username>
            <p>password: <input type=password name=password>
            <p><input type=submit value=Login>
        </form>
    '''


@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    return redirect(url_for('index'))
