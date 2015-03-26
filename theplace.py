import os
from flask.ext.migrate import MigrateCommand, Migrate, upgrade
from flask.ext.script import Manager

from application.app_settings import app, ROOT_DIR
from application.models import db

migrate = Migrate(app, db, directory=os.path.join(ROOT_DIR, "db/migrations"))
manager = Manager(app)
manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    app.run(threaded=True)



