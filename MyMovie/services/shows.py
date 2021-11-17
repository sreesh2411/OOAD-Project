from utils.conf import db
from bson.objectid import ObjectId
SHOWTIMES = [
   "9:AM","12:PM","3:PM","6:PM","9:PM"
]
ROOMS = list(range(10))

def get_allshows():
   coll = db.get_database("movie").get_collection("movies")
   data = list(coll.find({}))
   shows = []
   for d in data:
      if 'shows' in d:
         shows+=d['shows']
   return shows

def get_shows(mid):
   coll = db.get_database("movie").get_collection("movies")
   data = coll.find_one({"_id":ObjectId(mid)})
   return data['shows'] if 'shows' in data else []

def will_show_collide(show):
   shows = get_allshows()
   for s in shows:
      if s['room']==show['room'] and s['slot']==show['slot'] and s['date']==show['date']:
         return True
   return False

def will_showdate_collide(mid,showdate):
   shows = get_shows(mid)
   taken = [s for s in shows if s['date']==showdate]
   return len(taken)>0

def free_rooms(showdate,slot):
   shows = get_allshows()
   rooms = ROOMS.copy()
   for s in shows:
      if s['date']==showdate and s['slot']==slot:
         rooms.remove(s['room'])
   return rooms

def next_shownum(mid):
   shows = get_shows(mid)
   if not shows:
      return 0
   else:
      return max(shows,key=lambda w:w['id'])['id']+1

   
