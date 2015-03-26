from flask.ext.migrate import MigrateCommand, Migrate
from flask.ext.script import Manager

from application import app
from application.models import db

import application.views
import application.models
import application.assets

migrate = Migrate(app, db, directory="db/migrations")
manager = Manager(app)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()


