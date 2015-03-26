import os
from flask import Flask

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

app = Flask(__name__)
app.debug = True
app.threaded = True
app.config['SECRET_KEY'] = "!secret"
app.config['SAVE_PATH'] = '/mnt/homeworld/_IMAGES/_PPL' # os.path.join(ROOT_DIR, "media")



