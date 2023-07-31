from flask import Flask
from flask import Flask, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
from api import api

app.register_blueprint(api)



if __name__ == "__main__":
    app.run(debug=True)