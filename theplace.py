import os
from flask.ext.migrate import MigrateCommand, Migrate
from flask.ext.script import Manager

from application import app, ROOT_DIR
from application.models import db

import application.views
import application.models
import application.assets

migrate = Migrate(app, db, directory="db/migrations")
manager = Manager(app)
manager.add_command('db', MigrateCommand)

app.config['SAVE_PATH'] = '/mnt/homeworld/_IMAGES/_PPL' # os.path.join(ROOT_DIR, "media")

if __name__ == '__main__':
    manager.run()


