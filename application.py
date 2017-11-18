import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, jsonify

import shelve
import random
import json

# ############# database setup

DATABASE = 'database.db'

# EB looks for an 'application' callable by default.
application = Flask(__name__)

#
# application.config.from_object(__name__)
#
# # Load default config and override config from an environment variable
# application.config.update(dict(
#     DATABASE=os.path.join(application.root_path, 'database.db'),
#     SECRET_KEY='development key',
#     USERNAME='admin',
#     PASSWORD='default'
# ))
# application.config.from_envvar('APP_SETTINGS', silent=True)
#
#
# def connect_db():
#     """Connects to the specific database."""
#     rv = sqlite3.connect(application.config['DATABASE'])
#     rv.row_factory = sqlite3.Row
#     return rv
#
#
# def get_db():
#     """Opens a new database connection if there is none yet for the
#     current application context.
#     """
#     if not hasattr(g, 'sqlite_db'):
#         g.sqlite_db = connect_db()
#     return g.sqlite_db
#
#
# @application.teardown_appcontext
# def close_db(error):
#     """Closes the database again at the end of the request."""
#     if hasattr(g, 'sqlite_db'):
#         g.sqlite_db.close()
#
#
# def init_db():
#     db = get_db()
#     with application.open_resource('schema.sql', mode='r') as f:
#         db.cursor().executescript(f.read())
#     db.commit()
#
#
# @application.cli.command('initdb')
# def initdb_command():
#     """Initializes the database."""
#     init_db()
#     print('Initialized the database.')

# ############## GAME SETUP ##################

def create_game():
    """Commander begins the game setup process with this command

    :return game_code
    """
    num = random.randint(10, 1000)
    # print(num)
    #return str(num)
    data = {"game_code": num}
    return jsonify(data)


@application.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'GET':
        return create_game()


def pickle_post():
    db = shelve.open("spam")
    db['eggs'] = 'eggooo'
    return "posted"


def pickle_get():
    db = shelve.open("spam")
    a = "fail"
    try:
        if db.__contains__('eggs'):
            a = db['eggs']
    finally:
        db.close()
    return a
    # return "failure"


def create_account(username):
    """POST

    Players create their accounts once the game code has been sent out

    :param game_code
    :param username

    :return: user_id
    """

    return jsonify({username: "Created", "user_id": 0})


@application.route('/create_acct', methods=['GET', 'POST'])
def create_acct():
    if request.method == 'POST':
        dat = request.get_json()
        if "game_id" in dat and "username" in dat:
            return create_account(dat["username"])
        else:
            return "fail"
        # return create_account(request.args.get("game_id"))
    else:
        return error_message()


def get_number_of_players():
    """Commander can see how many players have logged into the session so far

    :return: number_of_players
    """


def start_game():
    """

    Once all the players have created accounts, the commander can start the game"""
    pass


# ############## COMMANDER ##################

def set_state():
    """ Set overall ship health, machine healths, and machine assignments
    :param: ship_health
    :param: machine_healths
    :param: current_tasks [task_id, user_id, machine_id]
    """
    pass


def get_task_status():
    """
    :param: task_id
    :return: task_status
    """
    pass

# ############## PLAYER ##################


def get_state():
    """

    :return: ship_health: (0 < ship_health <= 25)
    :return: array of machine healths (5x machines with health 5 = 25 health maximum)
    :return: array of current tasks [task_id, user_id, machine_id]

    task_id is a unique integer which increments as new tasks are generated
    """
    return "<h1>GAME STATUS</h1>\n"


def set_task_status():
    """POST the result (true or false) to the task_id on the server

    :param: task_id
    :param: True (success) / False (failure)

    """
    pass

# ############## GENERAL UTILITIES ###################


def error_message():
    err = {"ERROR": "Invalid Request"}
    return jsonify(err)


# # print a nice greeting.
# def say_hello(username = "World"):
#     return '<p>Hello %s!</p>\n' % username
#
#
#
# def do_the_login():
#     return "LOGGING IN -- POST"
#
#
# def show_the_login_form():
#     return "THIS IS THE LOGIN FORM -- GET"

# some bits of text for the page.
header_text = '''
    <html>\n<head> <title>CS65 Final Project Server</title> </head>\n<body>'''
instructions = '''
    <p><em>Hint</em>: This is a RESTful web service! Append a username
    to the URL (for example: <code>/Thelonious</code>) to say hello to
    someone specific.</p>\n'''
home_link = '<p><a href="/">Back</a></p>\n'
footer_text = '</body>\n</html>'



# # add a rule for the index page.
# application.add_url_rule('/', 'index', (lambda: header_text +
#     say_hello() + instructions + footer_text))
#
# # /status displays the ship status
# application.add_url_rule('/state', "get_game_state", get_game_state)


# @application.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         return do_the_login()
#     else:
#         return show_the_login_form()


# # add a rule when the page is accessed with a name appended to the site
# # URL.
# application.add_url_rule('/<username>', 'hello', (lambda username:
#     header_text + say_hello(username) + home_link + footer_text))


# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.debug = True
    application.run()
