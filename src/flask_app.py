import logging
from pkgutil import get_data
import flask
from flask import request

LOGGER = logging.getLogger("Flask")

# class WebApp:

#     def __init__(self, database):
#         self.db = database

#         self.app = flask.Flask(__name__)

#     # a simple page that says hello
#     @self.app.route('/', methods=['GET', 'POST'])
#     def hello(self):
#         print(data)
#         if request.method == 'POST':
#             data.update(request.form)
#         return flask.render_template('index.html', **data)

# Couldn't put this in HTML file becuase of the jinja template.
# <!-- {{'%0.2f'|format(product_details.UnitPrice|float)}} formatting a 2 decimal float -->

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

    # Status parameters set by the running program.
    "current_temp": 0.0,  # sentinel value of 0.0
    "current_humidity": 111,  # sentinel value of 111
    "cooling_status": "off",
    "fault_condition": "none",
}


def set_database(db):
    global database
    database = db
    LOGGER.debug(f"db set: {database}")


def get_database():
    global database
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


"""
Flask interface?
"""


def create_app():

    app = flask.Flask(__name__)

    @app.route('/', methods=['GET'])
    def index_get():
        db = get_database()

        # Render Jinja template.
        return flask.render_template('index.html',
                                     **convert_bools_to_html_checkbox_values(db))

    @app.route('/', methods=['POST'])
    def index_post():
        # Transform form data from strings into desired datatypes.
        # TODO: temperature field can be 'None' which crashes flask.
        input_data_mapping = {
            # Form search uses the 'name' of the html element.
            "sp": float(request.form["sp"]),
            "threshold": float(request.form["threshold"]),
            "controller_enabled": get_form_checkbox_bool(request.form, "http_enabled"),
        }
        db = get_database()
        db.update(input_data_mapping)
        return flask.redirect('/')

    @app.route('/clearfaults', methods=['POST'])
    def clear_faults():
        db = get_database()
        db.update({"fault_condition": ""})
        return flask.redirect('/')

    return app


def run_app(app, host_on_lan, no_reload):
    LOGGER.debug("starting flask server")
    # Note: can't use 'debu=True' because signal only works in the main thread of the
    # interpreter.'
    app.run(host="0.0.0.0" if host_on_lan else None,
            use_reloader=False if no_reload else None)
