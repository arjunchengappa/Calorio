from flask import Flask

from setup import setup_app

app = Flask(__name__)
setup_app(app)


if __name__ == '__main__':
    app.run()
