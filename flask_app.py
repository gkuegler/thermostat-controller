import flask

from flask import request

class WebApp:
    def __init__(self, database):
        self.db = database
        
        app = flask.Flask(__name__)

    # a simple page that says hello
    @app.route('/', methods=['GET', 'POST'])
    def hello(self):
        print(data)
        if request.method == 'POST':
            data.update(request.form)
        return flask.render_template('index.html', **data)


if __name__ == "main":
    data = {
    "temperature": 78,
    "threshold": 1,
    "timeout": 30,
    "enabled": False,
}

    app.run()
