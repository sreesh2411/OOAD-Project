from pymongo import MongoClient
from os import environ
import pymongo
db  = MongoClient(environ["MONGODB"])
print(db.movie.movies.index_information())
print(db.movie.movies.create_index([("Title",pymongo.TEXT)],name="search_index"))

SESSION_COOKIE_NAME = "sess"
SESSION_MONGODB = db
SESSION_MONGODB_DB = "movie"
SESSION_MONGODB_COLLECT = "session"
SESSION_TYPE = "mongodb"
SECRET_KEY="lord8266"
print("Intialized DB")
