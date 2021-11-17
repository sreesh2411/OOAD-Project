from utils.conf import db
from utils.helpers import hash_password
from flask import g
from bson.objectid import ObjectId

class User:
   def __init__(self,data):
      self.data = data

   @classmethod
   def from_id(cls,uid):
      user = db.movie.users.find_one({"_id":ObjectId(uid)})
      return User(user)
   
   @staticmethod
   def add_user(email,password):
      insert_id = db.movie.users.insert_one({
         "email":email,
         "password":hash_password(password)
      }).inserted_id
      return User.from_id(insert_id)

   @staticmethod
   def email_exists(email):
      return db.movie.users.find_one({"email":email}) is not None

   @classmethod
   def login(cls,email,password):
      password = hash_password(password)
      obj = db.movie.users.find_one({
         "email":email,
         "password":password
      })
      if obj:
         return cls(obj)
   
   def update(self):
      coll = db.get_database("movie").get_collection("users")
      coll.replace_one({"_id":self.data['_id']},self.data)

