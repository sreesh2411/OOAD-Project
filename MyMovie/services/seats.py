from utils.conf import db
from bson.objectid import ObjectId
import services.shows
import models.movie
import models.user
import flask
def can_book(tmat,tickets):
   for (i,j) in tickets:
      if 0<=i<len(tmat) and j not in tmat[i]:
         return False
   return True

def compute_price(tickets,cost):
   tcost = 0
   for (i,j) in tickets:
      tcost+=cost*(1+i/3)
   return tcost

def book_tickets(mid,sid,tickets):
   tickets = [(int(s[0]),int(s[1])) for s in tickets ]
   m =models.movie.Movie.get_movie(mid)
   show = m.data['shows'][sid]
   tmat = show['tickets']
   if not can_book(tmat,tickets):
      return False
   tcost = compute_price(tickets,show['price'])
   user = flask.g.user
   booking = {
      'mid':mid,
      'sid':sid,
      'tickets':tickets,
      'cost':tcost,
      'showdate':show['date'],
      'name':m.data['Title']
   }
   existing = False
   for b in user.data['bookings']:
      if b['mid']==booking['mid'] and b['sid']==booking['sid']:
         b['tickets'] = b['tickets'] + booking['tickets']
         b['cost'] = b['cost'] + booking['cost']
         existing = True
   if not existing:
      user.data['bookings'] = user.data.get('bookings',[])+[booking]
   user.update()
   for (i,j) in tickets:
      tmat[i].remove(j)
   m.update()
   return booking

def cancel_booking(bid):
   booking = flask.g.user.data['bookings'][bid]
   m = models.movie.Movie.get_movie(booking['mid'])
   s = m.data['shows'][booking['sid']]
   for (i,j) in booking['tickets']:
      s['tickets'][i].append(j)
   m.update()
   flask.g.user.data['bookings'].pop(bid)
   flask.g.user.update()


