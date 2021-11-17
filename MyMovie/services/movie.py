from utils.conf import db
from bson.objectid import ObjectId
import services.shows
import models.movie
import models.user
import flask

def get_all_movies():
   movies = list(db.get_database("movie").get_collection("movies").find({}))
   return movies

def add_movie(imdbid):
   movies = get_all_movies()
   for m in movies:
      if m['imdbID']==imdbid:
         return m,False
   m = models.movie.Movie.from_imdbid(imdbid)
   db.get_database("movie").get_collection("movies").insert_one(m.data)
   return m,True

def remove_movie_bookings(mid):
   users = db.get_database("movie").get_collection("users").find({})
   for u in users:
      bookings = u.get("bookings",[])
      u['bookings'] =[b for b in bookings if b['mid']!=mid]
      models.user.User(u).update()
   
def remove_show_bookings(mid,sid):
   users = db.get_database("movie").get_collection("users").find({})
   for u in users:
      bookings = u.get("bookings",[])
      u['bookings'] =[b for b in bookings if b['mid']!=mid or b['sid']!=sid]
      models.user.User(u).update()

