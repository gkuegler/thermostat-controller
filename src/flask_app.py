import logging
from pkgutil import get_data
import flask
from flask import request

import data

LOGGER = logging.getLogger("Flask")
LOGGER.setLevel(logging.INFO)

DEFAULT_PORT = 5000

# Default data for html template, used for testing when app is loaded 'create_app' by
# flask. Flask module automatically calls 'create_app' before if name==main block runs.
database = {
    # User controlled parameters.
    "host": "10.0.0.10",
    "port": 80,
    "sp": 67,
    "threshold": 3,
    "sample_period": 10,  # FUTURE
    "sample_count": 3,  # no. of smaples to average
    "http_enabled": False,  # master enable/disable
    "controller_enabled": False,
    "min_runtime": 5,  # min
    "max_runtime": 25,  # min TODO: rename to 'limit'
    "fault_condition": "none",
}


def set_database(db):
    global database
    database = db
    LOGGER.debug(f"db set: {id(database)}")


def get_database():
    global database
    LOGGER.debug(f"db get: {id(database)}")
    return database


def type_map(v):
    # TODO: utilize parameter type safety via inflection.
    if isinstance(v, bool):
        return "checked" if v else ""
    else:
        return v


def convert_bools_to_html_checkbox_values(d) -> dict:
    return {k: type_map(v) for k, v in d.items()}


def get_form_checkbox_bool(form, name):
    """This is absolute insanity on the part of HTML forms.
    Form doesn't return the name at all if the checkbox was checked and returns
    a "0" if the checkbox was checked. 'NoneType' is returned from '.get()' if
    not found."""
    return True if form.get(name) == 'on' else False


def create_app():

    app = flask.Flask(__name__)

    @app.route('/', methods=['GET'])
    def index_get():
        db = get_database()

        # Render Jinja template.
        return flask.render_template(
            'index.html', **(convert_bools_to_html_checkbox_values(db) | data.data))

    @app.route('/', methods=['POST'])
    def index_post():
        # Transform form data from strings into desired datatypes.
        # TODO: temperature field can be 'None' which crashes flask.
        settings = {
            # Form search uses the 'name' of the html element.
            "sp":
                float(request.form["sp"]),
            "threshold":
                float(request.form["threshold"]),
            "controller_enabled":
                get_form_checkbox_bool(request.form, "controller_enabled"),
        }
        db = get_database()
        db.update(settings)
        return flask.redirect('/')

    @app.route('/clearfaults', methods=['POST'])
    def clear_faults():
        db = get_database()
        db.update({"fault_condition": ""})
        return flask.redirect('/')

    @app.route('/temperature', methods=['GET'])
    def parameter_get_temperature():
        t = data.data["current_temp"]
        content = f"{t:.2f}"
        print(content)
        return flask.Response(f"{t:.2f}", content_type="text/plain")

    return app


def run_app(app, host_on_lan, no_reload, port=DEFAULT_PORT):
    LOGGER.debug("starting flask server")
    # Note: can't use 'debu=True' because signal only works in the main thread of the
    # interpreter.'
    app.run(host="0.0.0.0" if host_on_lan else None,
            port=port,
            use_reloader=False if no_reload else None)
