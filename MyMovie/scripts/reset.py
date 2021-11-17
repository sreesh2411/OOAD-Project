from pymongo import MongoClient,DeleteMany,DeleteOne,InsertOne
from dotenv import load_dotenv
from pathlib import Path
from os import environ
from json import load
from bson import json_util
load_dotenv(Path.cwd().parent/".env",override=True)
   
print(environ["MONGODB"])

client = MongoClient(environ["MONGODB"])

db=client.get_database("movie")

movies = db.get_collection("movies")
users = db.get_collection("users")
movies.delete_many({})

movie_data = json_util.loads(open("movie3.json").read())

movies.insert_many(movie_data)

for u in users.find({}):
   u['bookings'] = []
   users.replace_one({'_id':u['_id']},u)
