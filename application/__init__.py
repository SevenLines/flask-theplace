import os
from flask import Flask

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = "!secret"


