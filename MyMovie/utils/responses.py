import json
from bson import ObjectId
from bson import json_util
from flask import make_response

def bjson(data):
   resp = make_response(json_util.dumps(data))
   resp.headers['Content-Type'] = 'application/json'
   return resp

def error(err,status_code=403,details=None):
   obj = {"err":err}
   if details:
      obj['details'] = details
   resp = bjson(obj)
   resp.status_code = status_code
   return resp

def success(text,data=None):
   res = {"result":text}
   if data:
      res['data'] = data
   return bjson(res)