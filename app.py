#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
from sqlalchemy import inspect
import datetime as dt
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.hybrid import hybrid_property
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *

from models import (db, ArtistsGenresJunction,
                    VenuesGenresJunction,
                    Venues,
                    Areas,
                    Artists,
                    Genres,
                    Shows)
                      # importing db is new
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
#db = SQLAlchemy(app)
db.init_app(app)
migrate = Migrate(app, db)


# DONE: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # DONE: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.

  data = Areas.query.all()
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # DONE: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  search_term=request.form.get('search_term', '')
  qr = Venues.query.filter(Venues.name.ilike(f'%{search_term}%'))
  cnt = qr.count()
  data = qr.all()

  response = {'count': cnt,
              'data': data}
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # DONE: replace with real venue data from the venues table, using venue_id

    venue = Venues.query.get(venue_id)

    venue_genre_names = []
    for genre in venue.genres:
        venue_genre_names.append(genre.name)

    venue_all_shows = Shows.query.filter_by(venue_id=venue.id)
    venue_past_shows = venue_all_shows.filter(Shows.start_time<dt.datetime.utcnow())
    venue_upcoming_shows = venue_all_shows.filter(Shows.start_time>dt.datetime.utcnow())

    past_shows_count = venue_past_shows.count()
    upcoming_shows_count = venue_upcoming_shows.count()

    past_shows_data_list = []
    for past_show in venue_past_shows:
        past_show_dic = {'artist_id': past_show.artist.id,
                        'artist_name': past_show.artist.name,
                        'artist_image_link': past_show.artist.image_link,
                        'start_time': str(past_show.start_time)}
        past_shows_data_list.append(past_show_dic)

    upcoming_shows_data_list = []
    for upcoming_show in venue_upcoming_shows:
        upcoming_show_dic = {'artist_id': upcoming_show.artist.id,
                        'artist_name': upcoming_show.artist.name,
                        'artist_image_link': upcoming_show.artist.image_link,
                        'start_time': str(upcoming_show.start_time)}
        upcoming_shows_data_list.append(upcoming_show_dic)

    venue_data = {'id': venue.id,
        'name': venue.name,
        'genres': venue_genre_names,
        'address': venue.address,
        'city': venue.area.city,
        'state': venue.area.state,
        'phone': venue.phone,
        'website': venue.website,
        'facebook_link': venue.facebook_link,
        'seeking_talent': venue.seeking_talent,
        'seeking_description': venue.seeking_description,
        'image_link': venue.image_link,
        'past_shows': past_shows_data_list,
        'upcoming_shows': upcoming_shows_data_list,
        'past_shows_count': past_shows_count,
        'upcoming_shows_count': upcoming_shows_count}

    return render_template('pages/show_venue.html', venue=venue_data)
#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # DONE: insert form data as a new Venue record in the db, instead
  # DONE: modify data to be the data object returned from db insertion

    # on successful db insert, flash success

    # DONE: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

    area_exist = not (Areas.query.filter(Areas.state.ilike(request.form['state'])
                    , Areas.city.ilike(request.form['city'])).count() == 0)


    if not area_exist:
        # adding the area to session if entered area is not in database
        add_area = Areas(city=request.form['city'].title(),
                         state=request.form['state'].upper())
        db.session.add(add_area)


    genre_exist = not (Genres.query.filter(Genres.name.ilike(\
                       request.form['genres'])).count() == 0)

    if not genre_exist:
        # adding the genre to session if entered genre is not in database
        add_genre = Genres(name=request.form['genres'].title())
        db.session.add(add_genre)

    new_venue_area = Areas.query.filter(Areas.city.ilike(request.form['city']),\
                                Areas.state.ilike(request.form['state'])).first()

    new_venue_genre = Genres.query.filter(Genres.name.ilike(request.form['genres'])).all()

    error = False
    try:
        add_venue = Venues(name=request.form['name'],
                           address=request.form['address'],
                           phone=request.form['phone'],
                           facebook_link=request.form['facebook_link'],
                           genres=new_venue_genre,
                           area=new_venue_area
                           )
        db.session.add(add_venue)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
    finally:
        db.session.close()
    if error:
        flash(f'An error occurred. Venue {request.form["name"]} could not be listed.')
    else:
        flash(f'Venue {request.form["name"]} is successfully listed')

    return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # DONE: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    try:
        venue = Venues.query.get(venue_id)
        db.session.delete(venue)
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()


    return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # DONE: replace with real data returned from querying the database
  data = Artists.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
    # DONE: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    search_term = request.form.get("search_term")
    artist_query = Artists.query.filter(
                    Artists.name.ilike(f'%{search_term}%'))
    results_count = artist_query.count()

    artist_data = []
    for artist in artist_query.all():
        artist_num_upcoming_shows = db.session.query(Shows).\
        filter(Shows.artist_id==artist.id).\
        filter(Shows.start_time>dt.datetime.utcnow()).count()
        artist_dict = {'id': artist.id,
                       'name': artist.name,
                       'num_upcoming_shows': artist_num_upcoming_shows
                       }
        artist_data.append(artist_dict)

    response = {'count': results_count,
                'data': artist_data}

    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # DONE: replace with real artist data from the artist table, using artist_id

    artist = Artists.query.filter_by(id=artist_id).first()
    all_shows_qry = db.session.query(Shows).filter(Shows.artist_id==artist_id)

    upcoming_shows_qry = all_shows_qry.filter(Shows.start_time>dt.datetime.utcnow())
    past_shows_qry = all_shows_qry.filter(Shows.start_time<dt.datetime.utcnow())

    upcoming_shows_count = upcoming_shows_qry.count()
    past_shows_count = past_shows_qry.count()

    data_upcoming_shows = []
    for upcoming_show in upcoming_shows_qry.all():
        upcoming_show_dict = {'venue_id': upcoming_show.venue_id,
                              'venue_name': upcoming_show.venue.name,
                              'venue_image_link': upcoming_show.venue.image_link,
                              'start_time': str(upcoming_show.start_time)}
        data_upcoming_shows.append(upcoming_show_dict)

    data_past_shows = []
    for past_show in past_shows_qry.all():
        past_show_dict = {'venue_id': past_show.venue_id,
                              'venue_name': past_show.venue.name,
                              'venue_image_link': past_show.venue.image_link,
                              'start_time': str(past_show.start_time)}
        data_past_shows.append(past_show_dict)

    genres_names = []
    for genre in artist.genres:
        genres_names.append(genre.name)

    data = {'id': artist.id,
            'name': artist.name,
            'genres': genres_names,
            'city': artist.city,
            'state': artist.state,
            'phone': artist.phone,
            'facebook_link': artist.facebook_link,
            'website': artist.website,
            'seeking_venue': artist.seeking_venue,
            'image_link': artist.image_link,
            'past_shows': data_past_shows,
            'upcoming_shows': data_upcoming_shows,
            'past_shows_count': past_shows_count,
            'upcoming_shows_count': upcoming_shows_count
            }

    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist_fake={
      "id": 4,
      "name": "Guns N Petals",
      "genres": ["Rock n Roll"],
      "city": "San Francisco",
      "state": "CA",
      "phone": "326-123-5000",
      "website": "https://www.gunsnpetalsband.com",
      "facebook_link": "https://www.facebook.com/GunsNPetals",
      "seeking_venue": True,
      "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
      "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
      }

    artist = Artists.query.get(artist_id)


    # DONE: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # DONE: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    artist = Artists.query.get(artist_id)


    genre_exist = not (Genres.query.filter(Genres.name.ilike(\
                     request.form['genres'])).count() == 0)

    if not genre_exist:
        # adding the genre to session if entered genre is not in database
        add_genre = Genres(name=request.form['genres'].title())
        db.session.add(add_genre)

    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']

    try:
        db.session.commit()
    except:
        db.session.rollback()
        flash('Something went wrong')
    finally:
        db.session.close()

    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()

    venue = Venues.query.get(venue_id)

    # DONE: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # DONE: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes

    area_exist = not (Areas.query.filter(Areas.state.ilike(request.form['state'])
                        , Areas.city.ilike(request.form['city'])).count() == 0)

    if not area_exist:
        # adding the area to session if entered area is not in database
        add_area = Areas(city=request.form['city'].title(),
                         state=request.form['state'].upper())
        db.session.add(add_area)

    genre_exist = not (Genres.query.filter(Genres.name.ilike(\
                       request.form['genres'])).count() == 0)

    if not genre_exist:
        # adding the genre to session if entered genre is not in database
        add_genre = Genres(name=request.form['genres'].title())
        db.session.add(add_genre)

    venue = Venues.query.get(venue_id)
    venue.name = request.form['name']
    venue.address = request.form['address']
    venue.phone = request.form['phone']
    genre = Genres.query.filter_by(name = request.form['genres']).first()
    venue.genres = [genre]

    areaa = Areas.query.filter(Areas.state.ilike(request.form['state'])
                        , Areas.city.ilike(request.form['city'])).first()

    venue.area = areaa
    venue.facebook_link = request.form['facebook_link']

    try:
        db.session.commit()
    except:
        db.session.rollback()
        flash('Something went wrong')
    finally:
        db.session.close()
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # DONE: insert form data as a new Artist record in the db, instead
    # DONE: modify data to be the data object returned from db insertion

    genre_exist = not (Genres.query.filter(Genres.name.ilike(\
                       request.form['genres'])).count() == 0)

    if not genre_exist:
        # adding the genre to session if entered genre is not in database
        add_genre = Genres(name=request.form['genres'].title())
        db.session.add(add_genre)

    new_artist = Artists(name=request.form['name'],
                         city=request.form['city'],
                         state=request.form['state'],
                         phone=request.form['phone'],
                         facebook_link=request.form['facebook_link'])

    genres = Genres.query.filter_by(name = request.form['genres']).all()
    new_artist.genres = genres

    error = False
    try:
        db.session.add(new_artist)
        db.session.commit()
        db.session.refresh(new_artist)
    except:
        error = True
        db.session.rollback()
        flash(f'An error occurred. Artist {request.form["name"]}'\
              f'could not be listed')
    finally:
        db.session.close()

    if not error:
        flash(f'Artist {request.form["name"]} was successfully listed!')

    # on successful db insert, flash success

    # DONE: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')

    if error:
        return render_template('pages/home.html')
    else:
        return redirect(url_for('show_artist', artist_id=new_artist.id))


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # DONE: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.

  all_shows = Shows.query.all()

  data = []
  for show in all_shows:
      show_dict = {'venue_id': show.venue_id,
                   'venue_name': show.venue.name,
                   'artist_id': show.artist_id,
                   'artist_name': show.artist.name,
                   'artist_image_link': show.artist.image_link,
                   'start_time': str(show.start_time)}
      data.append(show_dict)


  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # DONE: insert form data as a new Show record in the db, instead


    error = False
    try:
        show = Shows(artist_id = request.form['artist_id'],
                     venue_id = request.form['venue_id'],
                     start_time = request.form['start_time'])
        db.session.add(show)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        flash('An error occurred. Show could not be listed')
    finally:
        db.session.close()

    if not error:
        flash('Show was successfully listed!')

    # on successful db insert, flash success

    # DONE: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
