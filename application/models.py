import os
from flask.ext.sqlalchemy import SQLAlchemy
from application import app, ROOT_DIR

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///%s' % os.path.join(ROOT_DIR, 'db/database.db')
db = SQLAlchemy(app)


class Source(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    url = db.Column(db.String(80))


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    local_url = db.Column(db.String(80))

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'local_url': self.local_url,
        }

    def __repr__(self):
        return '<Category: %r %r>' % (self.name, self.local_url)