from functools import wraps
from flask import render_template,url_for,redirect,session,request,g
from utils.conf import db
from utils.responses import error
from utils.helpers import validate_email,validate_password
from models.user import User

def set_user():
   uid = session['userid']
   g.user = User.from_id(uid)
   g.admin = g.user.data and 'admin' in g.user.data and g.user.data['admin']
   
def is_admin():
   return hasattr(g,'admin') and g.admin

def is_logged_in():
   if 'userid' not in session:
      return False
   return True

def check_logged_in(f):
   @wraps(f)
   def dfunc(*args,**kwargs):
      if 'userid' not in session:
         return redirect(url_for("login"))
      return f(*args,**kwargs)
   return dfunc

def api_check_logged_in(f):
   @wraps(f)
   def dfunc(*args,**kwargs):
      if not is_logged_in():
         return error("Need to be logged in",403)
      return f(*args,**kwargs)
   return dfunc

def check_valid_signup_body(f):
   @wraps(f)
   def dfunc(*args,**kwargs):
      print("here")
      if request.json is None:
         return error("Body must be JSON")
      body = request.json
      if 'email' not in body or 'password' not in body:
         return error("Invalid body")
      if not validate_email(body['email']):
         return error("Invalid Email")
      if not validate_password(body['password']):
         return error("Invalid Password")
      return f(*args,**kwargs)
   return dfunc

def check_admin(f):
   @wraps(f)
   def dfunc(*args,**kwargs):
      if not is_admin():
         return redirect("/")
      return f(*args,**kwargs)
   return dfunc

def api_check_admin(f):
   @wraps(f)
   def dfunc(*args,**kwargs):
      if not is_admin():
         return error("Need to be an admin",403)
      return f(*args,**kwargs)
   return dfunc


def check_email_exists(f):
   @wraps(f)
   def dfunc(*args,**kwargs):
      body = request.json
      user = db.movie.users.find_one({"email":body['email']})
      print("User email",user)
      if user:
         return error("Email exists")
      return f(*args,**kwargs)
   return dfunc