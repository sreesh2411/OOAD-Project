# Load Env
from dotenv import load_dotenv
from pathlib import Path
load_dotenv(override=True)

# Load Flask
from flask import request,Flask,render_template,g,redirect,url_for,make_response
from flask import session
from flask_session import Session
app = Flask(__name__,static_folder=str(Path.cwd()/"static"),static_url_path="/static")
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config.from_object("utils.conf")
Session(app)

# Load middleware
from middleware.auth import check_logged_in,check_email_exists,check_valid_signup_body,set_user,is_logged_in,is_admin
from middleware.auth import api_check_admin,api_check_logged_in,check_admin
from middleware.common import allow_post_json,to_datetime,simple_error,api_simple_error
import services
import services.seats
import services.movie


# Load models
from models.user import User
from models.movie import Movie

# Others
from utils.responses import error,bjson,success
from utils.conf import db
from bson.objectid import ObjectId
#filters
@app.template_filter()
def sort_shows(shows):
   return sorted(shows,key=lambda w:w['date'])

@app.before_request
def init():
   app.jinja_env.globals['admin'] = False 
   if is_logged_in():
      set_user()
      app.jinja_env.globals['admin'] = g.admin

@app.after_request
def headers(resp):
   resp.headers['What'] = '1'
   resp.headers['Access-Control-Allow-Headers'] = '*'
   return resp 

# Routes
@app.route("/login",methods=["GET"])
def login():
   return render_template("login.html",user='lord8266',title="Login to MyMovie")

@app.route("/api/signup",methods=["POST"])
@check_valid_signup_body
@check_email_exists
def api_signup():
   body = request.json
   email = body['email']
   password = body['password']
   user = User.add_user(email,password)
   print(user.data)
   session['userid'] = user.data['_id']
   return bjson(user.data)


@app.route("/api/login",methods=["POST"])
@check_valid_signup_body
def api_login():
   body = request.json
   user = User.login(body['email'],body['password'])
   if not user:
      return error("User not found")
   session['userid'] = user.data['_id']
   print(user)
   return bjson(user.data)

@app.route("/",methods=["GET"])
@check_logged_in
def index():
   return render_template("movies.html",title="MyMovie")

@app.route("/logout",methods=["GET"])
@check_logged_in
def logout():
   session.clear()
   resp = make_response("Ok")
   resp.set_cookie('sess', '')
   print("here")
   return resp

#api route
@app.route("/search",methods=["POST"])
@allow_post_json
@api_check_logged_in
def search_movies():
   term =  request.json['term'] if 'term' in request.json else ''
   if not term:
      return bjson(Movie.list_movies())
   else:
      return bjson(Movie.search_movies(term))

@app.route("/movie/<id>",methods=["GET"])
@check_logged_in
@simple_error
def look_movie(id):
   m = Movie.get_movie(id)
   if not m:
      return redirect(url_for("index"))
   return render_template("movie_page.html",movie=m)

#tickets route
@app.route("/tickets",methods=["GET"])
@check_logged_in
def tickets_page():
   return render_template("mytickets.html",booking=g.user.data.get("bookings",[]))


#show route
@app.route("/movie/<mid>/<sid>",methods=["GET"])
@check_logged_in
@simple_error
def show_page(mid,sid):
   sid = int(sid)
   m = Movie.get_movie(mid)
   if 0<=sid<len(m.data['shows']):
      return render_template("show_page.html",m=m,show=m.data['shows'][sid])
   else:
      return redirect(url_for("look_movie",id=mid))

@app.route("/movie/api/<mid>/<sid>",methods=["GET"])
@api_check_logged_in
@api_simple_error
def api_showdata(mid,sid):
   sid = int(sid)
   m = Movie.get_movie(mid)
   if 'shows' not in m.data:
      return error("Show not found",404)
   elif 0<=sid<len(m.data['shows']):
      return bjson(m.data)
   else:
      return error("Show not found",404)
#bookseats
@app.route("/movie/<mid>/<sid>/book",methods=["POST"])
@allow_post_json
@api_check_logged_in
@api_simple_error
def book_ticket(mid,sid):
   sid = int(sid)
   m = Movie.get_movie(mid)
   if 'shows' not in m.data or not 0<=sid<len(m.data['shows']):
      return error("Show doesnt exist")
   show = m.data['shows'][sid]
   tickets = request.json['tickets']
   booking = services.seats.book_tickets(mid,sid,tickets)
   if booking:
      return success("Ticket booked",data=booking)
   else:
      return error("Some of the tickets are not available",403)
#Admin

@app.route("/movie/<id>/addshow",methods=["GET"])
@check_admin
@simple_error
def add_show_page(id):
   m = Movie.get_movie(id)
   if not m:
      return redirect(url_for("index"))
   if not is_admin():
      return redirect(url_for("index"))
   return render_template("addshow.html",movie=m)

@app.route("/movie/<id>/addshow",methods=["POST"])
@api_check_admin
@allow_post_json
@api_simple_error
def add_show(id):
   m = Movie.get_movie(id)
   slot = request.json['slot']
   showdate = to_datetime(request.json['date'])
   room = int(request.json['room'])
   price = int(request.json['price'])
   if m.add_show(showdate,slot,room,price):
      return success("ok")
   else:
      return error("failed to add movie",503)

@app.route("/movie/<id>/shows",methods=["GET"])
@api_check_logged_in
@api_simple_error
def list_shows(id):
   m = Movie.get_movie(id)
   if not m:
      return error("Movie not found")
   return bjson(m.get_shows())

#Validate routes
@app.route("/movie/<id>/will_showdate_collide",methods=["POST"])
@allow_post_json
@api_check_admin
@api_simple_error
def will_showdate_collide(id):
   m = Movie.get_movie(id)
   if not m:
      return error("Not admin")
   if not is_admin():
      return error("Not admin")
   d = to_datetime(request.json['date'])
   return bjson({"result":services.shows.will_showdate_collide(id,d)})

@app.route("/movie/<id>/free_rooms",methods=["POST"])
@allow_post_json
@api_check_admin
@api_simple_error
def free_rooms(id):
   m = Movie.get_movie(id)
   if not m:
      return error("Not admin")
   if not is_admin():
      return error("Not admin")
   d = to_datetime(request.json['date'])
   slot = request.json['slot']
   return bjson({"result":services.shows.free_rooms(d,slot)})

#movie
@app.route("/addmovie",methods=["GET"])
@check_admin
@simple_error
def addmovie_page():
   return render_template("addmovie.html")

@app.route("/searchid/<iid>",methods=["GET"])
@api_check_admin
@api_simple_error
def search_imdbid(iid):
   m = Movie.from_imdbid(iid)
   if not m:
      return error("Not found",404)
   else:
      return bjson(m.data)

@app.route("/addmovie/<id>",methods=["POST"])
@api_check_admin
@api_simple_error
def addmovie_post(id):
   res = services.movie.add_movie(id)
   if res:
      return success("Added movie",{
         'data':res[0].data,'new':res[1]
      })
   else:
      return error("Movie could not be found",403)

@app.route("/remove/<mid>",methods=["POST"])
@api_check_admin
@api_simple_error
def remove_movie(mid):
   m = Movie.get_movie(mid)
   db.get_database("movie").get_collection("movies").delete_one({"_id":ObjectId(mid)})
   services.movie.remove_movie_bookings(mid)
   return {"result":"ok"}

@app.route("/remove/<mid>/<sid>",methods=["POST"])
@api_check_admin
@api_simple_error
def remove_show(mid,sid):
   sid = int(sid)
   m = Movie.get_movie(mid)
   if not 0<=sid<len(m.data['shows']):
      return error("Show doesnt exist")
   m.data['shows'].pop(sid)
   m.update()
   services.movie.remove_show_bookings(mid,sid)
   return {"result":"ok"}


@app.route("/cancel/<bid>",methods=["POST"])
@api_check_logged_in
@api_simple_error
def cancel_booking(bid):
   bid = int(bid)
   print("this is ",bid)
   bookings = g.user.data.get("bookings",[])
   if not 0<=bid<len(bookings):
      return error("Booking not found",404)
   else:
      services.seats.cancel_booking(bid)
      return {"result":"ok"}

app.run(debug=True,port=8080)
