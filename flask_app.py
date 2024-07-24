import flask

from flask import request

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

# Used for testing.
# Valid kv pairs need to be defined before it's used because flask debugging
# launcher automatically calls 'create_app' before if name==main block runs.
database = {
    "sp": 78,
    "threshold": 1,
    "timeout": 30,
    "http_enabled": False,
    "current_temp": 0,
}


def set_database(db):
    global database
    database = db
    print(f"db set: {database}")


def get_db():
    global database
    return database


def type_map(v):
    if isinstance(v, bool):
        return "checked" if v else ""
    else:
        return v


def convert_py_datatypes_to_html_datatypes(d) -> dict:
    return {k: type_map(v) for k, v in d.items()}


def get_form_checkbox_value(form, name):
    """This is absolute insanity on the part of HTML forms.
    Form doesn't return the name at all if the checkbox was checked and returns a "0" if the checkbox was checked.
    'NoneType' is returned from '.get()' if not found."""
    return True if form.get(name) == 'on' else False


def create_app():
    global database

    app = flask.Flask(__name__)

    # a simple page that says hello
    @app.route('/', methods=['GET'])
    def index_get():
        db = get_db()
        return flask.render_template(
            'index.html', **convert_py_datatypes_to_html_datatypes(db))

    @app.route('/', methods=['POST'])
    def index_put():
        print(request.form)
        # print("is html enabled: " + request.form.get("http_enabled"))
        enabled = True if request.form.get("http_enabled") == 0 else False
        data_mapping = {
            # "host": "10.0.0.10",
            # "port": 80,
            "sp": float(request.form["sp"]),
            "threshold": float(request.form["threshold"]),
            "http_enabled": get_form_checkbox_value(request.form,
                                                    "http_enabled")
        }
        db = get_db()
        db.update(data_mapping)
        # print(db)
        return flask.redirect('/')

    return app


def run_app(app, lan_enabled, no_reload):
    print("starting server")
    app.run(host="0.0.0.0" if lan_enabled else None,
            use_reloader=False if no_reload else None)


if __name__ == "main":
    pass
    # data = {
    #     "temperature": 78,
    #     "threshold": 1,
    #     "timeout": 30,
    #     "http_enabled": False,
    # }

    # set_database(data)
    # app = create_app()
    # app.run()
