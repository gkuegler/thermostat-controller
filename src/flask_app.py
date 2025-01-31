import logging
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
    "sp": 78,
    "threshold": 1,
    "timeout": 30,
    "http_enabled": False,
    "current_temp": 0,
    "cooling_status": "off",
}


def set_database(db):
    global database
    database = db
    LOGGER.debug(f"db set: {database}")


def get_database():
    global database
    return database


def type_map(v):
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
    global database

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
            "http_enabled": get_form_checkbox_bool(request.form, "http_enabled"),
            "min_runtime": int(request.form["min_runtime"]),
        }
        db = get_database()
        db.update(input_data_mapping)
        return flask.redirect('/')

    @app.route('/clearfaults', methods=['POST'])
    def clear_faults():
        db = get_database()
        db["fault_condition"] = ""
        return flask.redirect('/')

    return app


def run_app(app, lan_enabled, no_reload):
    LOGGER.debug("starting flask server")
    app.run(host="0.0.0.0" if lan_enabled else None,
            use_reloader=False if no_reload else None)


if __name__ == "main":
    pass
