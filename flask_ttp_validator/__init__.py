from flask import Flask
app = Flask(__name__, instance_relative_config=True)

import flask_ttp_validator.views
