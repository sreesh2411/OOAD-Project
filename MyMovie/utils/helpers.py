from hashlib import sha256
import re
import datetime
def hash_password(password):
   return sha256(password.encode()).hexdigest()

def validate_email(email):
   pat = r'^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$'
   mat = re.match(pat,email)
   return mat is not None

def validate_password(password):
   return len(password)>5

def check_min_datediff(d2,n=3):
   d1 = datetime.datetime.now()
   return (d2-d1).days>=n

