import os
from flask.ext.sqlalchemy import SQLAlchemy
from application.app_settings import app, ROOT_DIR

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///%s' % os.path.join(ROOT_DIR, 'db/database.db')
db = SQLAlchemy(app)


class Source(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    url = db.Column(db.String(80))


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    source_name = db.Column(db.String(80))
    local_id = db.Column(db.Integer)
    local_url = db.Column(db.String(80))

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'source_name': self.source_name,
            'local_url': self.local_url,
            'local_id': self.local_id
        }

    def __repr__(self):
        return '<Category: %r-%r %r>' % (self.local_id, self.name, self.local_url)