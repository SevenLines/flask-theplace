import os
from flask.ext.migrate import MigrateCommand, Migrate, upgrade
from flask.ext.script import Manager
from application.app_settings import app

from application import *
# from application.app_settings import app
# from application.models import db
#
# import application
#
# migrate = Migrate(app, db, directory="db/migrations")

manager = Manager(app)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
