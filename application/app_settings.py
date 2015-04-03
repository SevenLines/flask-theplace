import os
from flask import Flask
import yaml
import platform

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

config = {}
try:
    with open(os.path.join(ROOT_DIR, 'config.yml')) as f:
        config = yaml.load(f)
except BaseException as e:
    print e
    raise e

app = Flask(__name__)
app.debug = config.get('DEBUG', False)
app.threaded = True
app.config['SECRET_KEY'] = "!secret"
app.config['USE_LOCAL'] = config.get('USE_LOCAL', True)

if 'SAVE_PATH' in config:
    save_path = config['SAVE_PATH']
    if platform.system() == 'Windows':
        save_path = save_path.get('win', '.')
    else:
        save_path = save_path.get('unix', '.')
else:
    save_path = '.'

app.config['SAVE_PATH'] = save_path
app.config['ASSETS_DEBUG'] = config.get('ASSETS_DEBUG', False)




