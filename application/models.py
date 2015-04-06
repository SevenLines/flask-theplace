import os
from flask.ext.migrate import Migrate
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from application.app_settings import app, ROOT_DIR

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///%s' % os.path.join(ROOT_DIR, 'db/database.db')
db = SQLAlchemy(app)
migrate = Migrate(app, db, directory=os.path.join(ROOT_DIR, "db/migrations"))


class Setting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(20), index=True)
    value = db.Column(db.String(256))


class Album(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))

    album_id = db.Column(db.Integer)
    local_url = db.Column(db.String(80))

    source_id = db.Column(db.Integer, db.ForeignKey('source.id'))

    def __repr__(self):
        return "<Album: %s>" % (self.local_url)

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'album_id': self.album_id,
            'local_url': self.local_url
        }


class Source(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    local_id = db.Column(db.Integer)  # id of category in current source
    local_url = db.Column(db.String(80))

    albums = relationship("Album", backref='source', lazy='dynamic')
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))

    def __repr__(self):
        return "<Source: %s (%s)>" % (self.name, self.local_url)

    def serialize(self):
        out = {
            'name': self.name,
            'local_id': self.name,
            'local_url': self.name,
            'albums': [],
        }
        for album in self.albums.all():
            out['albums'].append(album.serialize())
        return out


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))

    sources = relationship("Source", backref='category', lazy='dynamic')
    # source_name = db.Column(db.String(80))
    # local_id = db.Column(db.Integer)
    # local_url = db.Column(db.String(80))

    def serialize(self):
        out = {
            'id': self.id,
            'name': self.name,
            'sources': []
        }
        for source in self.sources.all():
            out['sources'].append(source.serialize())
        return out

    def __repr__(self):
        return '<Category: %r: %r>' % (self.id, self.name)