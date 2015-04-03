import os
import random
import threading
import webbrowser
from flask.ext.migrate import MigrateCommand, Migrate
from flask.ext.script import Manager

from application.app_settings import app, ROOT_DIR
from application.models import db
# from application.socket_settings import socketio

manager = Manager(app)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    # socketio.run(app)
    if not app.debug:
        port = 5000 + random.randint(0, 999)
        url = "http://127.0.0.1:{0}".format(port)
        threading.Timer(1.25, lambda: webbrowser.open(url)).start()
        app.run(port=port, threaded=True)
    else:
        app.run(threaded=True)





