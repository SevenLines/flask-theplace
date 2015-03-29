import os
from flask.ext.migrate import MigrateCommand, Migrate
from flask.ext.script import Manager

from application.app_settings import app, ROOT_DIR
from application.models import db
from application.socket_settings import socketio

migrate = Migrate(app, db, directory=os.path.join(ROOT_DIR, "db/migrations"))
manager = Manager(app)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    # socketio.run(app)
    app.run(threaded=True)



