from functools import wraps
from flask import render_template,url_for,redirect,session,request,make_response
from utils.conf import db
from utils.responses import error
from dateutil import parser

def allow_post_json(f):
   @wraps(f)
   def dfunc(*args,**kwargs):
      try:
         method = request.method
         body = request.json
        
         if method!="POST" or body is None:
            return error("Invalid body")
         print("body is ",body)
         return f(*args,**kwargs)
      except Exception as e:
         print(e)
         return error("Invalid body")
   return dfunc

def to_datetime(d):
   return parser.isoparse(d)

def simple_error(f):
   @wraps(f)
   def dfunc(*args,**kwargs):
      try:
         return f(*args,**kwargs)
      except Exception as e:
         print(e)
         resp = make_response(render_template("simple_error.html",err=str(e)))
         resp.status_code = 503 
         return resp
   return dfunc

def api_simple_error(f):
   @wraps(f)
   def dfunc(*args,**kwargs):
      try:
         return f(*args,**kwargs)
      except Exception as e:
         print(e)
         return error(str(e),503)
   return dfunc