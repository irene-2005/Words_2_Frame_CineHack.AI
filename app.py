from flask import Flask
from ai.blueprint import bp as ai_bp


def create_app():
    app = Flask(__name__)
    app.register_blueprint(ai_bp)
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(port=5000, debug=True)
