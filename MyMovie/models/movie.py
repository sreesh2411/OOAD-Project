import utils.conf
from bson.objectid import ObjectId
import services.shows
import requests
import json
import utils.helpers

class Movie:
   def __init__(self, data):
      self.data = data

   @classmethod
   def from_stored(data):
      pass

   @staticmethod
   def list_movies(n=100):
      coll = utils.conf.db.get_database("movie").get_collection("movies")
      movies = list(coll.find({}, limit=n, projection={
          'locations': False
      }))
      return movies

   @classmethod
   def get_movie(cls, id):
      print(id)
      coll = utils.conf.db.get_database("movie").get_collection("movies")
      data = coll.find_one({'_id': ObjectId(id)})
      if not data:
         return None
      return cls(data)

   @staticmethod
   def search_movies(term, n=100):
      coll = utils.conf.db.get_database("movie").get_collection("movies")
      movies = list(coll.find({"Title": {
          "$regex": f'.*{term}.*',
          "$options":"i"
      }},
      limit=n,
      projection={
      'locations': False
      },
         #  sort=[('score', {'$meta': 'textScore'})]
      ))
      return movies
   
   def add_show(self,date,slot,room,price):
      show = {
         'id':services.shows.next_shownum(self.data['_id']),
         'date':date,
         'slot':slot,
         'room':room,
         'price':price,
         'tickets':[
            list(range(10)),list(range(10)),list(range(10)),list(range(10))
         ]
      }
      if price<100:
         return False
      if not utils.helpers.check_min_datediff(date):
         return False
      if services.shows.will_show_collide(show):
         return False
      elif services.shows.will_showdate_collide(self.data['_id'],date):
         return False
      else:
         self.data['shows'] = self.data.get('shows',[])+[show]
         self.update()
         return True
   
   def get_shows(self):
      return self.data['shows'] if 'shows' in self.data else []
   def update(self):
      coll = utils.conf.db.get_database("movie").get_collection("movies")
      coll.replace_one({"_id":self.data['_id']},self.data)

   @classmethod
   def from_imdbid(cls,iid):
      url = f'http://www.omdbapi.com/?i={iid}&apikey=9ea68fdf&plot=full'
      ret = requests.get(url)
      if ret.status_code!=200 or b'Error' in ret.content:
         return None
      data = json.loads(ret.content.decode())
      return cls(data)
