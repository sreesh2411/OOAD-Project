
from pymongo import MongoClient,DeleteMany,DeleteOne,InsertOne
from dotenv import load_dotenv
from pathlib import Path
from os import environ
from json import load
from bson import json_util

def get_movie_details(imdb_id):
    url = f'http://www.omdbapi.com/?i={imdb_id}&apikey={KEY}&plot=full'
    ret = requests.get(url)
    if ret.status_code!=200:
        print(ret.content)
        return {}
    else:
        return json.loads(ret.content.decode())


load_dotenv(Path.cwd().parent/".env",override=True)
   
print(environ["MONGODB"])

client = MongoClient(environ["MONGODB"])

db=client.get_database("movie")

movies = db.get_collection("movies")
users = db.get_collection("users")

movie_data = list(movies.find({}))

d = json_util.dumps(movie_data)
open("movie3.json","w").write(d)
