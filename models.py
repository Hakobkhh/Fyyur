from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.hybrid import hybrid_property


db = SQLAlchemy()
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

ArtistsGenresJunction = db.Table('ArtistsGenresJunction',
    db.Column('artist_id', db.Integer, db.ForeignKey('Artists.id'), primary_key=True),
    db.Column('genre_id', db.Integer, db.ForeignKey('Genres.id'), primary_key=True)
)

VenuesGenresJunction = db.Table('VenuesGenresJunction',
    db.Column('venue_id', db.Integer, db.ForeignKey('Venues.id'), primary_key=True),
    db.Column('genre_id', db.Integer, db.ForeignKey('Genres.id'), primary_key=True)
)


class Venues(db.Model):
    __tablename__ = 'Venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    address = db.Column(db.String(120))
    area_id = db.Column(db.Integer, db.ForeignKey('Areas.id'),
        nullable=False)
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean())
    seeking_description = db.Column(db.String(), nullable=True)
    image_link = db.Column(db.String(500))
    shows = db.relationship('Shows', backref='venue', lazy=True)
    genres = db.relationship('Genres', secondary=VenuesGenresJunction, lazy='subquery',
        backref=db.backref('venues', lazy=True))


    @hybrid_property
    def city(self):
        return self.area.city

    @hybrid_property
    def state(self):
        return self.area.state

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

    # DONE: implement any missing fields, as a database migration using Flask-Migrate

class Areas(db.Model):
    __tablename__ = 'Areas'
    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    venues = db.relationship('Venues', backref='area', lazy=True)

    def __repr__(self):
        return f'{self.city}, {self.state}'


class Artists(db.Model):
    __tablename__ = 'Artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean())
    seeking_description = db.Column(db.String(), nullable=True)
    image_link = db.Column(db.String(500))
    shows = db.relationship('Shows', backref='artist', lazy=True)
    genres = db.relationship('Genres', secondary=ArtistsGenresJunction, lazy='subquery',
        backref=db.backref('artists', lazy=True))

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

    # DONE: implement any missing fields, as a database migration using Flask-Migrate

class Genres(db.Model):
    __tablename__ = 'Genres'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

class Shows(db.Model):
    __tablename__ = 'Shows'
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venues.id'),
        nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artists.id'),
        nullable=False)

    def __repr__(self):
        return (f'----------- Show -----------\n'
                f'Start time: {self.start_time}\n'
                f'Artist: {self.artist.name}\n'
                f'Venue: {self.venue.name}\n')

# DONE Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
