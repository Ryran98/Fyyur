#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from models import db, Venue, Artist, Show
import sys

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
app.app_context().push()

# TODO: (DONE) connect to a local postgresql database
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

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
  venues = Venue.query.all()
  places = Venue.query.distinct(Venue.city, Venue.state).all()
  data = []

  for place in places:
    data.append({
      'city': place.city,
      'state': place.state,
      'venues': [{
        'id': venue.id,
        'name': venue.name,
        'num_upcoming_shows': len([show for show in venue.shows if show.start_time > datetime.now()])
      } for venue in venues if venue.city == place.city and venue.state == place.state]
    })

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form['search_term']
  venues = Venue.query.filter(Venue.name.ilike("%"+ search_term +"%"))
  data = []

  for venue in venues:
    data.append({
      'id': venue.id,
      'name': venue.name,
      'num_upcoming_shows': len([show for show in venue.shows if show.start_time > datetime.now()])
    })

  response= {
    "count": len(data),
    "data": data
  }

  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.get(venue_id)
  if (venue is None):
    flash('Venue id ' + str(venue_id) + ' does not exist.')
    return render_template('pages/home.html')

  past_shows = []
  upcoming_shows = []

  for show in venue.shows:
    formatted_show = {
        'artist_id': show.artist.id,
        'artist_name': show.artist.name,
        'artist_image_link': show.artist.image_link,
        'start_time': show.start_time.strftime("%Y-%m-%dT%H:%M:%S.000Z")
      }
    if show.start_time < datetime.now():
      past_shows.append(formatted_show)
    else:
      upcoming_shows.append(formatted_show)

  data = {
    'id': venue.id,
    'name': venue.name,
    'genres': venue.genres,
    'address': venue.address,
    'city': venue.city,
    'state': venue.state,
    'phone': venue.phone,
    'website': venue.website,
    'facebook_link': venue.facebook_link,
    'seeking_talent': venue.seeking_talent,
    'seeking_description': venue.seeking_description,
    'image_link': venue.image_link,
    'past_shows': past_shows,
    'upcoming_shows': upcoming_shows,
    'past_shows_count': len(past_shows),
    'upcoming_shows_count': len(upcoming_shows)
  }

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  try:
    venue = Venue(name=request.form.get('name', ''))
    venue.city = request.form.get('city', '')
    venue.state = request.form.get('state', '')
    venue.address = request.form.get('address', '')
    venue.phone = request.form.get('phone', '')
    venue.image_link = request.form.get('image_link', '')
    venue.genres = request.form.getlist('genres')
    venue.facebook_link = request.form.get('facebook_link', '')
    venue.website = request.form.get('website_link', '')
    venue.seeking_talent = request.form.get('seeking_talent', 'n') == 'y'
    venue.seeking_description = request.form.get('seeking_description', '')

    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + venue.name + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
    flash('Venue id ' + venue_id + ' was successfully deleted.')
  except:
    db.session.rollback
    flash('An error occurred. Venue id ' + venue_id + ' could not be deleted.')
  finally:
    db.session.close()
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  artists = Artist.query.all()
  data = []

  for artist in artists:
    data.append({
      'id': artist.id,
      'name': artist.name
    })
  
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form.get('search_term', '')
  artists = Artist.query.filter(Artist.name.ilike("%"+ search_term + "%"))
  data = []

  for artist in artists:
    data.append({
      'id': artist.id,
      'name': artist.name,
      'num_upcoming_shows': len([show for show in artist.shows if show.start_time > datetime.now()])
    })

  response={
    "count": len(data),
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = Artist.query.get(artist_id)
  if (artist is None):
    flash('Artist id ' + str(artist_id) + ' does not exist.')
    return render_template('pages/home.html')

  past_shows = []
  upcoming_shows = []

  for show in artist.shows:
    formatted_show = {
        'venue_id': show.venue.id,
        'venue_name': show.venue.name,
        'venue_image_link': show.venue.image_link,
        'start_time': show.start_time.strftime("%Y-%m-%dT%H:%M:%S.000Z")
      }
    if show.start_time < datetime.now():
      past_shows.append(formatted_show)
    else:
      upcoming_shows.append(formatted_show)

  data = {
    'id': artist.id,
    'name': artist.name,
    'genres': artist.genres,
    'city': artist.city,
    'state': artist.state,
    'phone': artist.phone,
    'website': artist.website,
    'facebook_link': artist.facebook_link,
    'seeking_venue': artist.seeking_venue,
    'seeking_description': artist.seeking_description,
    'image_link': artist.image_link,
    'past_shows': past_shows,
    'upcoming_shows': upcoming_shows,
    'past_shows_count': len(past_shows),
    'upcoming_shows_count': len(upcoming_shows)
  }

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.get(artist_id)
  if (artist is None):
      flash('Artist id ' + str(artist_id) + ' does not exist.')
      return render_template('pages/home.html')

  form = ArtistForm(obj=artist)
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  try:
    artist = Artist.query.get(artist_id)
    if (artist is None):
      flash('Artist id ' + str(artist_id) + ' does not exist.')
      return render_template('pages/home.html')

    artist.name = request.form.get('name', '')
    artist.city = request.form.get('city', '')
    artist.state = request.form.get('state', '')
    artist.phone = request.form.get('phone', '')
    artist.image_link = request.form.get('image_link', '')
    artist.genres = request.form.getlist('genres')
    artist.facebook_link = request.form.get('facebook_link', '')
    artist.website = request.form.get('website_link', '')
    artist.seeking_venue = request.form.get('seeking_venue', 'n') == 'y'
    artist.seeking_description = request.form.get('seeking_description', '')
    db.session.commit()
    flash('Artist ' + artist.name + ' was successfully updated.')
  except:
    db.session.rollback()
    flash('An error occurred. Artist id ' + str(artist_id) + ' could not be updated.')
  finally:
    db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.get(venue_id)
  if (venue is None):
      flash('Venue id ' + str(venue_id) + ' does not exist.')
      return render_template('pages/home.html')

  form = VenueForm(obj=venue)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  try:
    venue = Venue.query.get(venue_id)
    if (venue is None):
      flash('Venue id ' + str(venue_id) + ' does not exist.')
      return render_template('pages/home.html')
    
    venue.name = request.form.get('name', '')
    venue.city = request.form.get('city', '')
    venue.state = request.form.get('state', '')
    venue.address = request.form.get('address', '')
    venue.phone = request.form.get('phone', '')
    venue.image_link = request.form.get('image_link', '')
    venue.genres = request.form.getlist('genres')
    venue.facebook_link = request.form.get('facebook_link', '')
    venue.website = request.form.get('website_link', '')
    venue.seeking_talent = request.form.get('seeking_talent', 'n') == 'y'
    venue.seeking_description = request.form.get('seeking_description', '')
    db.session.commit()
    flash('Venue ' + venue.name + ' was successfully updated.')
  except:
    db.session.rollback()
    flash('An error occurred. Venue id ' + str(venue_id) + ' could not be updated.')
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
  try:
    artist = Artist(name=request.form.get('name', ''))
    artist.city = request.form.get('city', '')
    artist.state = request.form.get('state', '')
    artist.phone = request.form.get('phone', '')
    artist.image_link = request.form.get('image_link', '')
    artist.genres = request.form.getlist('genres')
    artist.facebook_link = request.form.get('facebook_link', '')
    artist.website = request.form.get('website_link', '')
    artist.seeking_venue = request.form.get('seeking_venue', 'n') == 'y'
    artist.seeking_description = request.form.get('seeking_description', '')

    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  shows = Show.query.all()
  data = []

  for show in shows:
    data.append({
      'venue_id': show.venue.id,
      'venue_name': show.venue.name,
      'artist_id': show.artist.id,
      'artist_name': show.artist.name,
      'artist_image_link': show.artist.image_link,
      'start_time': show.start_time.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    })

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  try:
    artist_id = request.form.get('artist_id', '')
    venue_id = request.form.get('venue_id', '')
    artist = Artist.query.get(artist_id)
    venue = Venue.query.get(venue_id)

    if (artist is None):
      flash('No artist could be found for ID ' + artist_id)
      return render_template('pages/home.html')
    if (venue is None):
      flash('No venue could be found for ID ' + venue_id)
      return render_template('pages/home.html')
    
    show = Show(artist=artist, venue=venue, start_time=request.form['start_time'])
    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()
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
