import os
# import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, jsonify, make_response

import shelve
import random
import json

# SELF NOTES FROM 7pm Saturday brainstorm sesh
# generate_event() (commander service calls this if we can't add random server events)

# get_state()
#
# return: running (t/f), win (t/f), component_health_list (0-5,0-5,0-5,0-5,0-5), assignments
# where each assignment is a pair [player_id, machine_id]

# add_assignment()
# param: player_id, machine_id

# add_task_result()
# param: pass/fail (t/f)
# param: machine_id

#


# ############# database setup

DATABASE = 'database.db'

# EB looks for an 'application' callable by default.
application = Flask(__name__)


def clear_and_restart():
    db = shelve.open(DATABASE)
    db["players"] = []
    db["running"] = True
    db["win"] = False
    db["machine_health_arr"] = [5, 5, 5, 5, 5]
    db["assignments"] = []
    db["counter"] = 0


def check_if_everything_is_initialized():
    db = shelve.open(DATABASE)
    if "players" not in db.keys():
        db["players"] = []

    if "running" not in db.keys():
        db["running"] = True

    if "win" not in db.keys():
        db["win"] = False

    if "machine_health_arr" not in db.keys():
        db["machine_health_arr"] = [5, 5, 5, 5, 5]

    if "assignments" not in db.keys():
        db["assignments"] = []

    if "counter" not in db.keys():
        db["counter"] = 0


# ############## GAME SETUP ##################

@application.route('/create_game', methods=['GET', 'POST'])
def create():
    if request.method == 'GET':
        return create_game()


def create_game():
    """Commander begins the game setup process with this command

    :return game_code
    """

    # reset all existing data to defaults
    clear_and_restart()

    num = random.randint(10, 1000)
    # print(num)
    # return str(num)
    data = {"game_code": num}
    return jsonify(data)

# def pickle_post():
#     db = shelve.open("spam")
#     db['eggs'] = 'eggooo'
#     return "posted"
#
#
# def pickle_get():
#     db = shelve.open("spam")
#     a = "fail"
#     try:
#         if db.__contains__('eggs'):
#             a = db['eggs']
#     finally:
#         db.close()
#     return a
#     # return "failure"


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


def create_account(username):
    """POST

    Players create their accounts once the game code has been sent out

    :param game_code
    :param username

    :return: user_id
    """
    db = shelve.open(DATABASE)

    if "players" not in db.keys():
        db["players"] = []

    username_list = db["players"]
    if username in username_list:
        return jsonify({"STATUS": "FAILURE"})

    username_list.append(username)
    db["players"] = username_list

    return jsonify({"STATUS": "SUCCESS", "user_id": len(username_list) - 1})


@application.route('/number_of_players', methods=['GET', 'POST'])
def num_players():
    if request.method == 'GET':
        return get_number_of_players()
    else:
        return error_message()


def get_number_of_players():
    """Commander can see how many players have logged into the session so far

    :return: number_of_players
    """
    db = shelve.open(DATABASE)

    if "players" not in db.keys():
        db["players"] = []

    return jsonify({"number_of_players": len(db["players"])})


@application.route('/start_game', methods=['GET', 'POST'])
def start():
    if request.method == 'GET':
        return start_game()
    else:
        return error_message()


def start_game():
    """

    Once all the players have created accounts, the commander can start the game

    :return player_list"""

    db = shelve.open(DATABASE)

    if "players" not in db.keys():
        db["players"] = []

    return json.dumps({"username_list": [ob for ob in db["players"]]})


@application.route('/get_state', methods=['GET', 'POST'])
def gs():
    if request.method == 'GET':
        return get_state()
    else:
        return error_message()


def get_state():
    """

    :return: ship_health: (0 < ship_health <= 25)
    :return: array of machine healths (5x machines with health 5 = 25 health maximum)
    :return: array of current tasks [task_id, user_id, machine_id]

    task_id is a unique integer which increments as new tasks are generated
    """

    db = shelve.open(DATABASE)

    check_if_everything_is_initialized()

    state = jsonify({"running": db["running"],
                     "win": db["win"],
                     "machine_health_arr": db["machine_health_arr"],
                     "assignments": db["assignments"],
                     "counter": db["counter"]})

    return state


# ############## COMMANDER ##################

# def set_state():
#     """ Set overall ship health, machine healths, and machine assignments
#     :param: ship_health
#     :param: machine_healths
#     :param: current_tasks [task_id, user_id, machine_id]
#     """
#     pass


def get_task_status():
    """
    :param: task_id
    :return: task_status
    """
    pass

# ############## PLAYER ##################



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
