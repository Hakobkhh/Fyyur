import datetime as dt
import random
import sys
sys.path.append('..')
from app import (Areas, Venues, Artists, Genres, Shows, VenuesGenresJunction,
                ArtistsGenresJunction, db)

from data_lists import areas_list, genres_list, adj_list, \
                        place_suffix_list, related_genres_list, noun_list

def venue_factory(name_):
    """
    Create and return a Venues model object
    with a given name for testing purposes.
    Adds the name string to other attributes
    with corresponding keywords.

    Parameters:
    name_ (String): venue name

    Returns:
    venue (Venues): Venues model object
    """

    venue = Venues(
                  name=f'{name_}',
                  address=f'address: {name_}',
                  phone=f'phone: {name_}',
                  website=f'website: {name_}',
                  facebook_link=f'facebook_link: {name_}',
                  seeking_talent=True,
                  seeking_description='we are seeking artists',
                  image_link=f'image_link: {name_}')

    return venue

def artist_factory(name_):
    """
    Create and return an Artists model object
    with a given name for testing purposes.
    Adds the name string to other attributes
    with corresponding keywords.

    Parameters:
    name_ (String): artist name

    Returns:
    artist (Artists): Artists model object
    """
    artist = Artists(
                  name=f'{name_}',
                  city=f'city: {name_}',
                  state=f'state: {name_}',
                  phone=f'phone: {name_}',
                  website=f'website: {name_}',
                  facebook_link=f'facebook_link: {name_}',
                  seeking_venue=True,
                  seeking_description='we are seeking venues',
                  image_link=f'image_link: {name_}')
    return artist

def create_genres(genres_list=genres_list):
    """
    Reads geners_list and adds listed geners to
    the database for testing purposes.

    Parameters:
    geners_list (list): list of strings with geners names

    Returns:
    created_genres (tuple): a tuple with created Genres model objects


    """
    created_genres = []
    for genre in genres_list:
        new_genre = Genres(name=genre)
        db.session.add(new_genre)
        created_genres.append(new_genre)
    db.session.commit()

    return tuple(created_genres)


def clear_table(model):
    """
    clear the table of the given model
    """
    for itm in db.session.query(model).all():
        db.session.delete(itm)
    db.session.commit()

    if hasattr(model, '__tablename__'):
        print(f'{model.__tablename__} cleared')
    elif hasattr(model, 'name'):
        print(f'{model.name} cleared')
    else:
        print('something went wrong')

def clear_all_tables():
    """
    clear all given tables
    """
    clear_table(Genres)
    clear_table(Shows)
    clear_table(VenuesGenresJunction)
    clear_table(ArtistsGenresJunction)
    clear_table(Artists)
    clear_table(Venues)
    clear_table(Areas)

def create_areas(areas_list=areas_list):

    """
    Reads areas_list and adds listed areas to
    the database for testing purposes.

    Parameters:
    areas_list (list): list of tuples with area parameters (city, state)

    Returns:
    created_areas (tuple): a tuple with created Areas model objects

    """

    created_areas = []
    for area in areas_list:
        city, state = area
        new_area = Areas(city=city, state=state)
        db.session.add(new_area)
        created_areas.append(new_area)
    db.session.commit()
    return tuple(created_areas)


def get_rel_genres(genre, related_genres_list=related_genres_list):
    """
    return genre objects of given genre

    Parameters:
    genre (String): genre name

    Returns:
    genre objects (Genres): tupple of Genres objects
    """
    ret_genre_list = []
    for genre_tuple in related_genres_list:
        if genre in genre_tuple:
            for genre_iter in genre_tuple:
                genre_found = Genres.query.filter_by(name=genre_iter).first()
                ret_genre_list.append(genre_found)
    return tuple(ret_genre_list)

def create_venue():

    venues_names_list = []
    for venue_iter in Venues.query.all():
        venues_names_list.append(venue_iter.name)


    new_name_found = False
    while not new_name_found:
        area = random.choice(Areas.query.all())
        genre = random.choice(Genres.query.all())
        place_suffix = random.choice(place_suffix_list)

        new_venue_name = f'{area.city} {genre} {place_suffix}'
        if new_venue_name not in venues_names_list:
            new_name_found = True


    new_venue = venue_factory(new_venue_name)
    new_venue.area = area



    for related_genre in get_rel_genres(genre=genre.name):
        new_venue.genres.append(related_genre)

    db.session.add(new_venue)
    db.session.commit()
    return new_venue

def create_artist(adj_list=adj_list, noun_list=noun_list):
    artists_names_list = []
    for artist_iter in Artists.query.all():
        artists_names_list.append(artist_iter.name)

    new_name_found = False
    while not new_name_found:
        adj = random.choice(adj_list)
        noun = random.choice(noun_list)
        genre = random.choice(Genres.query.all())

        new_artist_name = f'{adj} {noun} {genre} band'


        if new_artist_name not in artists_names_list:
            new_name_found = True

    new_artist = artist_factory(new_artist_name)

    for related_genre in get_rel_genres(genre=genre.name):
        new_artist.genres.append(related_genre)

    db.session.add(new_artist)
    db.session.commit()
    return new_artist

def random_date():
    today = dt.datetime.today()
    current_day = today.day
    current_year = today.year
    current_month = today.month

    random_day = random.randint(current_day - 6, current_day + 5)
    random_hour = random.randint(19, 22)
    random_date = dt.datetime(day=random_day,
                              hour=random_hour,
                              year=current_year,
                              month=current_month)
    return random_date

def create_shows():

    for genre in Genres.query.all():
        for num_of_shows in range(0, random.randint(3, 6)):
            random_artist = random.choice(genre.artists)
            random_venue = random.choice(genre.venues)
            show = Shows(start_time=random_date())
            show.venue = random_venue
            show.artist = random_artist
            db.session.add(show)
    db.session.commit()

def generate_test_data(num_venues=7, num_artists=7):
    create_genres()
    create_areas()
    for i in range(1, num_venues):
        create_venue()

    for i in range(1, num_artists):
        create_artist()

    create_shows()

generate_test_data()

# qr = Venues.query.filter(Venues.name.ilike('%tal%'))
# cnt = qr.count()
# data = qr.all()
#
# response = {'count': cnt,
#             'data': data}
#
# for itm in response['data']:
#     print(type(itm))
