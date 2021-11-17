from pymongo import MongoClient,DeleteMany,DeleteOne,InsertOne
from dotenv import load_dotenv
from pathlib import Path
from os import environ
from json import load

load_dotenv(Path.cwd().parent/".env",override=True)
def get_required_fields(data):
   fields = ["Title","Year","Rated","Released","Runtime","Director","Actors","Plot","Language","Country","imdbID","Poster"]
   return {k:v for (k,v) in data.items() if k in fields}
   
print(environ["MONGODB"])

client = MongoClient(environ["MONGODB"])

db=client.movie

db.movies.delete_many({})

data = load(open("movies2.json"))
cnt = 0
failed = 0
for d in data:
   cnt+=1
   try:
      d = get_required_fields(d)
      db.movies.insert_one(d)
      print(cnt,d["imdbID"],failed)
   except Exception as e:
      print(e)
      failed+=1
print(failed/cnt)