from selenium import webdriver
import time
import math
import re
import requests
import json
import subprocess
from pathlib import Path
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from termcolor import colored, cprint

ROOT = "http://localhost:8080"
APILOGIN = "http://localhost:8080/api/login"
ADMIN = ["lordvishwa123@gmail.com", "Arduino123"]
NONADMIN = ["lord8266@a.com", 'Arduino123']


def get_driver():
   options = webdriver.ChromeOptions()
   # Path to your chrome profile
   # options.add_argument(
   #     '--user-data-dir=C:\\Users\\Vishwa\\AppData\\Local\\Google\\Chrome\\User Data')
   # options.add_argument('--profile-directory=Profile 1')
   w = webdriver.Chrome(
       executable_path="E:\SeleniumDrivers\chromedriver.exe",
       chrome_options=options)
   return w


def wait(n):
   time.sleep(n)


class MyMovieNavigator:
   def logged_in(self):
      return len(w.find_elements_by_id("logoutbtn")) > 0

   def login(self, username, password):
      w.get(ROOT)
      wait(0.3)
      if self.logged_in():
         w.find_element_by_id("logoutbtn").click()
         wait(0.5)
      w.find_element_by_id("inputEmail").send_keys(username)
      w.find_element_by_id("inputPassword").send_keys(password)
      w.find_element_by_id("lbtn").click()
      wait(2)
      if not self.logged_in():
         return False
      else:
         return True


class TestException(Exception):
   def __init__(self, err):
      super().__init__()
      self.err = err


def reset_db():
   proc = subprocess.Popen(
       "python ../scripts/reset.py",
       cwd=(Path.cwd().parent/"scripts").resolve(), shell=True, universal_newlines=True,
       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
   out, err = proc.communicate()
   return out


class BackendTestBase:
   def __init__(self):
      self.sess = requests.Session()
      self.login()

   def login(self):
      res = self.post_request(APILOGIN, {
          'email': ADMIN[0], 'password': ADMIN[1]
      })

   def post_request(self, url, data):
      res = self.sess.post(url, data=json.dumps(data), headers={
          'Content-Type': 'application/json'
      })
      return res

   def get_request(self, url):
      res = self.sess.get(url)
      return res


class ASeleniumTests:

   def list_movies(self):
      w.get(ROOT)
      wait(0.3)
      w.find_element_by_id("search_text").clear()
      w.find_element_by_id("search_movie").click()
      wait(0.5)
      l = len(w.find_elements_by_css_selector(".movieItem"))
      if l != 21:
         return False, f'Movie items found: {l}'
      else:
         return True, f'Movie items found: {l}'

   def search_term(self, term='avengers', n=3):
      w.find_element_by_id("search_text").clear()
      w.find_element_by_id("search_text").send_keys(term)
      w.find_element_by_id("search_movie").click()
      wait(0.5)
      l = len(w.find_elements_by_css_selector(".movieItem"))
      if l != n:
         return False, f'Movie items found: {l}'
      else:
         return True, f'Movie items found: {l}'

   def case_insenitive(self, term='avengers', n=3):
      t1 = self.search_term(term)
      t2 = self.search_term(term.upper())
      if not t1 and t2:
         return False, t1[1]+'\n'+t2[1]
      else:
         return True, t1[1]

   def noresults(self, term='2121212'):
      w.find_element_by_id("search_text").clear()
      w.find_element_by_id("search_text").send_keys(term)
      w.find_element_by_id("search_movie").click()
      wait(0.5)
      l = len(w.find_elements_by_css_selector(".movieItem"))
      if l:
         return False, f'Movie items found: {l}'
      else:
         return True, f'Movie items found: {l}'

   def select_movie(self):
      w.get(ROOT)
      wait(0.3)
      w.find_element_by_id("search_text").clear()
      w.find_element_by_id("search_movie").click()
      wait(0.5)
      m = w.find_elements_by_css_selector(".movieItem div")[3]
      m.click()
      wait(0.5)
      if re.search(r'/movie/.*', w.current_url):
         return True, f'Found {w.find_element_by_css_selector("h1").text}'
      else:
         return False, 'Could not load page'

   def run_tests(self):
      print(self.list_movies())
      print(self.search_term())
      print(self.case_insenitive())
      print(self.noresults())
      print(self.select_movie())


class ABackendAPITests(BackendTestBase):

   def search_movies(self, term=""):
      res = self.post_request("http://localhost:8080/search", {
          "term": term
      })
      content = json.loads(res.content.decode())
      return content

   def all_movies(self):
      c = self.search_movies()
      l = len(c)
      if len(c) != 21:
         return False, f'Movie items found: {l}'
      else:
         return True, f'Movie items found: {l}'

   def search_term(self):
      c = self.search_movies('avengers')
      l = len(c)
      if len(c) != 3:
         return False, f'Movie items found: {l}'
      else:
         return True, f'Movie items found: {l}'

   def case_insensitive(self):
      c1 = self.search_movies('avengers')
      c2 = self.search_movies('AVENGERS')
      if len(c1) != len(c2):
         return False, f'Movie items found: {len(c1)}, {len(c2)}'
      else:
         return True, f'Movie items found: {len(c1)}'

   def valid_route(self):
      res = self.sess.get(
          "http://localhost:8080/movie/60797618920c419d02d26e9d")
      res2 = self.sess.get(
          "http://localhost:8080/movie/60797618920c419d02d26e9dd")
      if res.status_code != 200 or res2.status_code != 503:
         return False, f'Found Status { res.status_code} { res2.status_code}'
      else:
         return True, 'Movie routes are handled correctly'

   def run_tests(self):
      self.login()
      print(self.all_movies())
      print(self.search_term())
      print(self.case_insensitive())
      print(self.valid_route())


class BSeleniumTests:

   def __init__(self, reset=True):
      if reset:
         reset_db()
         print("Reset DB")
      w.get("http://localhost:8080/movie/60797618920c419d02d26e9d")
      wait(1)

   def check_shows(self):
      show = w.find_elements_by_css_selector(".show")

      if not show:
         return False, 'Shows not found'
      else:
         show = show[0]
         return True, 'Show found '+show.text

   def select_show(self):
      show = w.find_elements_by_css_selector(".show")
      show = show[0]
      show.click()
      wait(0.5)
      if w.current_url[-2:] != '/0':
         return False, 'Show not selected'
      else:
         return True, 'Show is selected'

   def select_seats(self):
      seats = w.find_elements_by_css_selector(".seat")
      seatsi = [30, 31, 32]
      for s in seatsi:
         s = seats[s]
         s.click()
      wait(0.1)
      p = round(float(w.find_element_by_id("price").text))
      if p != 6000:
         return False, 'Price is not correct'
      else:
         return True, 'Price is correct'

   def book_tickets(self):
      b = w.find_element_by_id("bookb")
      b.click()
      wait(1)
      if w.current_url != "http://localhost:8080/tickets":
         return False, 'Ticket not booked'
      if w.find_elements_by_css_selector(".book"):
         return True, 'Ticket booked'
      return False, 'Booking not found'

   def check_seats_booked(self):
      w.get("http://localhost:8080/movie/60797618920c419d02d26e9d/0")
      wait(0.5)
      unavailables = w.find_elements_by_css_selector(".seat.unavailable")
      if len(unavailables) != 3:
         return False, 'Seats not blacked'
      else:
         return True, 'Seats are booked'

   def run_tests(self):
      print(self.check_shows())
      print(self.select_show())
      print(self.select_seats())
      print(self.book_tickets())
      print(self.check_seats_booked())


class BBackendAPITests(BackendTestBase):

   def __init__(self, reset=True):
      super().__init__()
      if reset:
         reset_db()
         print("Reset DB")

   def book_tickets(self):
      tickets = ["30", "31"]
      res = self.post_request(
          "http://localhost:8080/movie/60797618920c419d02d26e9d/0/book", {
              'tickets': tickets
          })
      if res.status_code != 200:
         return False, f'Received {res.status_code}: {res.content.decode()}'
      data = json.loads(res.content.decode())
      if data['data']['cost'] != 4000:
         return False, f"Received invalid price {data['price']}"
      return True, f'Received correct response {res.content.decode()}'

   def invalid_tickets(self):
      tickets = ["30", "-1-1"]
      res = self.post_request(
          "http://localhost:8080/movie/60797618920c419d02d26e9d/0/book", {
              'tickets': tickets
          })
      if res.status_code == 200:
         return False, f'Ticket booked for invalid input, Received {res.content.decode()}'
      elif res.status_code == 503:
         return True, f'Received correct error response {res.content.decode()}'
      else:
         return False, f'Recieved invalid status code {res.status_code}'

   def unavailable_tickets(self):
      tickets = ["30"]
      res = self.post_request(
          "http://localhost:8080/movie/60797618920c419d02d26e9d/0/book", {
              'tickets': tickets
          })
      if res.status_code == 200:
         return False, f'Ticket booked for invalid input, Received {res.content.decode()}'
      elif res.status_code == 403:
         return True, f'Received correct error response {res.content.decode()}'
      else:
         return False, f'Recieved invalid status code {res.status_code}'

   def check_tickets_booked(self):
      res = self.get_request(
          "http://localhost:8080/movie/api/60797618920c419d02d26e9d/0")
      if res.status_code != 200:
         return False, f'Received {res.status_code}: {res.content.decode()}'
      data = json.loads(res.content.decode())
      show = data['shows'][0]
      if 0 not in show['tickets'][3]:
         return True, f'Ticket confirmed to be booked'
      else:
         return False, 'Ticket was not booked'

   def run_tests(self):
      print(self.book_tickets())
      print(self.invalid_tickets())
      print(self.unavailable_tickets())
      print(self.check_tickets_booked())


class CSeleniumTest:

   def __init__(self, reset=True):
      if reset:
         reset_db()
         print("Reset DB")

   def check_admin_access(self):
      MyMovieNavigator().login(*NONADMIN)
      w.get("http://localhost:8080/addmovie")
      wait(0.5)

      if w.current_url == 'http://localhost:8080/addmovie':
         return False, 'Non Admin has invalid access'
      MyMovieNavigator().login(*ADMIN)
      w.get("http://localhost:8080/addmovie")
      wait(0.5)
      if w.current_url != 'http://localhost:8080/addmovie':
         return False, 'Admin doesnt have proper access'
      return True, 'Access is correct'

   def show_date_invalid(self):
      w.get("http://localhost:8080/movie/60797618920c419d02d26ea3/addshow")
      wait(0.5)
      w.execute_script(
          "document.getElementById('date').value=arguments[0]", '2021-04-19')
      w.find_element_by_css_selector(".selection button").click()
      wait(0.2)
      if (w.find_element_by_id("date").get_attribute("value") == ''):
         return True, 'Invalid date is not accepted'
      else:
         return False, 'Invalid date is accepted'

   def show_date_valid(self):
      w.execute_script(
          "document.getElementById('date').value=arguments[0]", '2021-04-22')
      wait(0.2)
      option = w.find_element_by_css_selector('#slot option[value="12:PM"]')
      option.click()
      wait(0.2)
      w.find_element_by_css_selector(".selection button").click()
      if (w.find_element_by_id("date").get_attribute("value") != ''):
         return True, 'Valid date is accepted'
      else:
         return False, 'Valid date is not accepted'

   def check_rooms(self):
      WebDriverWait(w, 5).until(EC.presence_of_element_located(
          (By.CSS_SELECTOR, "#room option")))
      l = w.find_elements_by_css_selector("#room option")
      if len(l) == 10:
         return True, 'All rooms are returned'
      else:
         return False, 'All rooms are not returned'

   def add_show(self):
      w.find_element_by_id("price").send_keys(500)
      w.find_element_by_id("addshow").click()
      wait(0.5)
      if w.current_url != 'http://localhost:8080/movie/60797618920c419d02d26ea3':
         return False, 'The show was not added'
      if w.find_elements_by_css_selector(".show"):
         return True, 'The show was added'
      return False, 'The show was not added'

   def remove_show(self):
      w.get("http://localhost:8080/movie/60797618920c419d02d26ea3/0")
      WebDriverWait(w, 5).until(EC.url_to_be(
          "http://localhost:8080/movie/60797618920c419d02d26ea3/0"))
      WebDriverWait(w, 2).until(
          EC.element_to_be_clickable((By.CSS_SELECTOR, "#remove_show"))).click()
      w.find_element_by_id("remove_show").click()
      try:
         WebDriverWait(w, 5).until(EC.url_to_be(
             "http://localhost:8080/movie/60797618920c419d02d26ea3"))
         return True, 'The show was removed'
      except TimeoutException:
         return False, 'The show was not removed'

   def add_movie(self):
      w.get("http://localhost:8080/addmovie")
      try:
         elem = WebDriverWait(w, 4).until(
             EC.element_to_be_clickable((By.CSS_SELECTOR, "#search")))
         w.find_element_by_id("imdbid").send_keys("tt4154796")
         elem.click()
         a = WebDriverWait(w, 4).until(
             EC.element_to_be_clickable((By.CSS_SELECTOR, "#addm")))
         a.click()
         return True, 'The movie was added'
      except TimeoutException:
         return False, 'The movie could not be added'

   def remove_movie(self):
      try:
         WebDriverWait(w, 4).until(EC.element_to_be_clickable(
             (By.CSS_SELECTOR, '#link'))).click()
         WebDriverWait(w, 4).until(EC.presence_of_element_located(
             (By.CSS_SELECTOR, '#removeMovie'))).click()
         WebDriverWait(w, 4).until(EC.url_to_be("http://localhost:8080/"))
         return True, 'The movie was removed'
      except TimeoutException:
         return False, 'The movie was not removed'

   def run_tests(self):
      print(self.check_admin_access())
      print(self.show_date_invalid())
      print(self.show_date_valid())
      print(self.check_rooms())
      print(self.add_show())
      print(self.remove_show())
      print(self.add_movie())
      print(self.remove_movie())


class CBackendAPITests(BackendTestBase):

   def __init__(self, reset=True):
      super().__init__()
      if reset:
         reset_db()
         print("Reset DB")

   def will_showdate_collide(self):
      mid = '60797618920c419d02d26e9d'
      res = self.post_request(f'http://localhost:8080/movie/{mid}/will_showdate_collide', {
          'date': '2021-04-22'
      })
      if res.status_code != 200:
         return False, 'Route isnt working'
      data = json.loads(res.content.decode())
      if data['result']:
         return True, 'Returned correct result'
      return False, 'Returned wrong result'

   def get_free_rooms(self):
      mid = '60797618920c419d02d26e9f'
      res = self.post_request(f'http://localhost:8080/movie/{mid}/free_rooms', {
          'date': '2021-04-22',
          'slot': '9:AM'
      })
      if res.status_code != 200:
         return False, 'Route isnt working'
      data = json.loads(res.content.decode())
      if sorted(data['result']) == [0, 1, 3, 4, 5, 6, 7, 8, 9]:
         return True, 'Returned correct result'
      return False, 'Returned wrong result'

   def add_show_valid(self):
      mid = '60797618920c419d02d26e9f'
      res = self.post_request(f'http://localhost:8080/movie/{mid}/addshow', {
          'date': '2021-04-22',
          'slot': '9:AM',
          'room': 0,
          'price': 500
      })
      if res.status_code != 200:
         return False, 'Route isnt working'
      data = json.loads(res.content.decode())
      if data['result'] == 'ok':
         return True, 'Show was added'
      return False, 'Show wasnt added'

   def add_show_existing(self):
      mid = '60797618920c419d02d26e9f'
      res = self.post_request(f'http://localhost:8080/movie/{mid}/addshow', {
          'date': '2021-04-22',
          'slot': '9:AM',
          'room': 0,
          'price': 500
      })
      if res.status_code != 200:
         return True, 'Existing show was identified'
      else:
         return False, 'Existing show was not identified'

   def add_movie_valid(self):
      tt = 'tt4154796'
      res = self.post_request(f'http://localhost:8080/addmovie/'+tt, {})
      if res.status_code == 200:
         return True, 'Movie was added successfully'
      else:
         return False, 'Movie was not added'

   def add_movie_invalid(self):
      tt = 'hahahsdd3w'
      res = self.post_request(f'http://localhost:8080/addmovie/'+tt, {})
      if res.status_code != 200:
         return True, 'Invalid Movie was identified'
      else:
         return False, 'Invalid Movie was not identified'

   def run_tests(self):
      print(self.will_showdate_collide())
      print(self.get_free_rooms())
      print(self.add_show_valid())
      print(self.add_show_existing())
      print(self.add_movie_valid())
      print(self.add_movie_invalid())


AS = [
    {
        'name': 'List All Movies',
        'desc': 'List all movies in the home page and check if all are shown',
        'func': ASeleniumTests.list_movies
    },
    {
        'name': 'Search for a term',
        'desc': 'Search for term "avengers" and verify results',
        'func': ASeleniumTests.search_term
    },
    {
        'name': 'Case Insensitive search',
        'desc': 'Make sure searches can be case insensitive',
        'func': ASeleniumTests.case_insenitive
    },
    {
        'name': 'A term not found',
        'desc': 'Make sure no results are returned when term doesnt match all movies',
        'func': ASeleniumTests.noresults
    },
    {
        'name': 'Select a movie',
        'desc': 'Select a movie and check if it shows more details about it when clicked',
        'func': ASeleniumTests.select_movie
    }
]
AB = [
    {
        'name': 'Search route: EMPTY TERM',
        'desc': 'Search for an empty and verify results ',
        'func': ABackendAPITests.all_movies
    },
    {
        'name': 'Search route: Avengers',
        'desc': 'Search for a term and verify results ',
        'func': ABackendAPITests.search_term
    },
    {
        'name': 'Search route: Case insensitive',
        'desc': 'Make sure searches are case insensitive ',
        'func': ABackendAPITests.case_insensitive
    },
    {
        'name': 'Movie routes ',
        'desc': 'Check a valid movie route and an invalid, verify results',
        'func': ABackendAPITests.valid_route
    }
]
BS = [
    {
        'name': 'Check Shows',
        'desc': 'Check if shows are displayed for a movie',
        'func': BSeleniumTests.check_shows
    },
    {
        'name': 'Select Show',
        'desc': 'Select a show and verify seat matrix is displayed',
        'func': BSeleniumTests.select_show
    },
    {
        'name': 'Select seats',
        'desc': 'Select seats and make sure the price displayed is correct',
        'func': BSeleniumTests.select_seats
    },
    {
        'name': 'Book seats',
        'desc': 'Book selected seats and make sure the booking is made',
        'func': BSeleniumTests.book_tickets
    },
    {
        'name': 'Check seats are booked',
        'desc': 'Verify that the seats booked are black when visiting it again',
        'func': BSeleniumTests.check_seats_booked
    }
]
BB = [
    {
        'name': 'Book ticket route',
        'desc': 'Request to book tickets which are available and valid, verify response',
        'func': BBackendAPITests.book_tickets
    },
    {
        'name': 'Book ticket route: Invalid tickets',
        'desc': 'Request to book tickets with invalid body, verify response',
        'func': BBackendAPITests.invalid_tickets
    },
    {
        'name': 'Book ticket route: Unavailable tickets',
        'desc': 'Request to book unavailable tickets, verify response',
        'func': BBackendAPITests.unavailable_tickets
    },
    {
        'name': 'Show route',
        'desc': 'Verify that booked tickets are really booked',
        'func': BBackendAPITests.check_tickets_booked
    }

]
CS = [
    {
        'name': 'Check Admin access',
        'desc': 'Login as different users, check that only admin can add movies',
        'func': CSeleniumTest.check_admin_access
    },
    {
        'name': 'Show date invalid',
        'desc': 'Select an invalid date and check if it isnt allowed',
        'func': CSeleniumTest.show_date_invalid
    },
    {
        'name': 'Show date valid',
        'desc': 'Select an valid date and check if doesnt allow it',
        'func': CSeleniumTest.show_date_valid
    },
    {
        'name': 'Check if rooms are available',
        'desc': 'Select show date and slot, verify if all rooms are returned',
        'func': CSeleniumTest.check_rooms
    },
    {
        'name': 'Add a show',
        'desc': 'Add show with required details, verify that it is added',
        'func': CSeleniumTest.add_show
    },
    {
        'name': 'Remove a show',
        'desc': 'Remove a show, verify that is removed',
        'func': CSeleniumTest.remove_show
    },
    {
        'name': 'Add a movie using imdb id',
        'desc': 'Add a movie, verify that is added',
        'func': CSeleniumTest.add_movie
    },
    {
        'name': 'Remove a movie',
        'desc': 'Remove a movie, verify that is removed',
        'func': CSeleniumTest.remove_movie
    },

]
CB = [
    {
        'name': 'will_showdate_collide',
        'desc': 'Verify that the same date cant be chosen for a show again',
        'func': CBackendAPITests.will_showdate_collide
    },
    {
        'name': 'get_free_rooms',
        'desc': 'Verify that all free rooms are returned for a particular date and slot',
        'func': CBackendAPITests.get_free_rooms
    },
    {
        'name': 'add_show_valid',
        'desc': 'Verify that a valid show is added',
        'func': CBackendAPITests.add_show_valid
    },
    {
        'name': 'add_show_existing',
        'desc': 'Verify that an exisiting show cant be added again',
        'func': CBackendAPITests.add_show_existing
    },
    {
        'name': 'add_movie_valid',
        'desc': 'Verify that a new movie can be added with imdb id',
        'func': CBackendAPITests.add_movie_valid
    },
    {
        'name': 'add_movie_invalid',
        'desc': 'Verify that a invalid movie is not added which doesnt exist in imdb',
        'func': CBackendAPITests.add_movie_invalid
    },

]

RUNNER = [
    {
        'usecase': 'Movie Listing and Selection',
        'cats': [
            {
                'cat': 'Backend Tests',
                'c': ABackendAPITests,
                'data': AB
            },
            {
                'cat': 'Selenium Tests',
                'c': ASeleniumTests,
                'data': AS
            }
        ]
    },
    {
        'usecase': 'Seat Selection and Booking',
        'cats': [
            {
                'cat': 'Backend Tests',
                'c': BBackendAPITests,
                'data': BB
            },
            {
                'cat': 'Selenium Tests',
                'c': BSeleniumTests,
                'data': BS
            }
        ]
    },
    {
        'usecase': 'Event Management',
        'cats': [
            {
                'cat': 'Backend Tests',
                'c': CBackendAPITests,
                'data': CB
            },
            {
                'cat': 'Selenium Tests',
                'c': CSeleniumTest,
                'data': CS
            }
        ]
    },
]
print("Loading Driver")
w = get_driver()
print("Loaded driver")

MyMovieNavigator().login(*ADMIN)

print("Press enter to continue")
input()

print("Resetting DB")
reset_db()
print("Reset DB")

s = ABackendAPITests()
i = 0
passed = 0
for r in RUNNER:
   usecase = r['usecase']
   print(usecase+"\n")
   for cat in r['cats']:
      # if cat['cat']!='Backend Tests' or usecase!='Event Management':
      #    break
      print(cat['cat']+"\n")
      c = cat['c']()
      for t in cat['data']:
         try:
            cprint(f"{i+1}: {t['name']}",'yellow')
            print(f"-> {t['desc']}")
            res, data = t['func'](c)
            print("Result: ", colored("PASSED",'green') if res else colored("FAILED",'red')),
            cprint(data,'green')
            passed+=1
         except Exception as e:
            cprint("Result: FAILED",'red')
            cprint(str(e),'red')
         print("\n--------------------------------------\n")
         i += 1
         # wait(2.5)
         
cprint("PASSED {} / {}".format(passed,i))
w.close()
