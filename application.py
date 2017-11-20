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
    # status is either {setup, running, win, lose}
    db["session_status"] = "setup"
    db["machine_health_arr"] = [5, 5, 5, 5, 5]
    db["assignments"] = []
    db["counter"] = 0


def check_if_everything_is_initialized():
    db = shelve.open(DATABASE)
    if "players" not in db.keys():
        db["players"] = []

    if "session_status" not in db.keys():
        db["session_status"] = "setup"

    if "machine_health_arr" not in db.keys():
        db["machine_health_arr"] = [5, 5, 5, 5, 5]

    if "assignments" not in db.keys():
        db["assignments"] = []

    if "counter" not in db.keys():
        db["counter"] = 0


# def game_over_check():
#     # db = shelve.open(DATABASE)
#
#     # calculate ship health
#     tot = 0
#     health_array = db["machine_health_arr"]
#     for h in health_array:
#         tot += h
#
#     # check if lose
#     if tot <= 0:
#         db["session_status"] = "lose"
#
#     # check if win
#     if tot >= 25:
#         db["session_status"] = "win"

# ############## GAME SETUP ##################


@application.route('/create_game', methods=['GET', 'POST'])
def create():
    if request.method == 'GET':
        return create_game()


def create_game():
    """Commander begins the game setup process with this command

    :return game_id
    """

    # reset all existing data to defaults
    clear_and_restart()

    db = shelve.open(DATABASE)

    # generate and save random number
    num = random.randint(10, 1000)
    db["game_id"] = num

    data = {"game_id": num}
    return jsonify(data)


@application.route('/create_acct', methods=['GET', 'POST'])
def create_acct():

    dat = request.get_json()
    if "game_id" in dat and "username" in dat:
        return create_account(dat["game_id"], dat["username"])
    else:
        return error_message("missing game_id and or username")
    # return create_account(request.args.get("game_id"))



def create_account(game_id, username):
    """POST

    Players create their accounts once the game code has been sent out

    :param game_id
    :param username

    :return: user_id
    """
    db = shelve.open(DATABASE)

    if "players" not in db.keys():
        db["players"] = []

    # check username
    username_list = db["players"]
    if username in username_list:
        return error_message("Username already in use.")

    # check game_id
    if not game_id.equals(db["game_id"]):
        return error_message("invalid game_id")

    username_list.append(username)
    db["players"] = username_list

    data_to_return = jsonify({"STATUS": "SUCCESS", "player_id": len(username_list) - 1})
    return data_to_return


@application.route('/number_of_players', methods=['GET', 'POST'])
def num_players():
    if request.method == 'GET':
        return get_number_of_players()
    else:
        return error_message("Must make a GET request")


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
        return error_message("Must make a GET request")


def start_game():
    """

    Once all the players have created accounts, the commander can start the game

    :return player_list"""

    db = shelve.open(DATABASE)
    check_if_everything_is_initialized()

    # start the game
    db["session_status"] = "running"

    # health
    db["machine_health_arr"] = [3, 3, 3, 3, 3]

    # increment counter
    db["counter"] += 1

    return jsonify({"username_list": [ob for ob in db["players"]]})


@application.route('/get_state', methods=['GET', 'POST'])
def gs():
    if request.method == 'GET':
        return get_state()
    else:
        return error_message("Must make a GET request")


def get_state():
    """

    :return: ship_health: (0 < ship_health <= 25)
    :return: array of machine healths (5x machines with health 5 = 25 health maximum)
    :return: array of current tasks [task_id, user_id, machine_id]

    task_id is a unique integer which increments as new tasks are generated
    """

    db = shelve.open(DATABASE)

    check_if_everything_is_initialized()

    state = jsonify({"session_status": db["session_status"],
                     "machine_health_arr": db["machine_health_arr"],
                     "assignments": db["assignments"],
                     "counter": db["counter"]})

    return state


# ############## COMMANDER ##################


@application.route('/commander_set_assignment', methods=['GET', 'POST'])
def assign():
    if request.method == 'POST':
        dat = request.get_json()
        if "player_id" in dat and "machine_id" in dat:
            return set_assignment(dat["player_id"], dat["machine_id"])
        else:
            return error_message("Missing player_id and or machine_id")
    else:
        return error_message("Must make a POST request")


def set_assignment(player_id, machine_id):
    """
    :param: task_id, player_id

    """
    db = shelve.open(DATABASE)
    check_if_everything_is_initialized()

    # increment counter
    db["counter"] += 1

    # check to see if player_id is within range
    if player_id < 0 or player_id >= len(db["players"]):
        return error_message("player_id out of range")

    # check to see if machine_id is within range
    if machine_id < 0 or machine_id > 4:
        return error_message("machine_id out of range")

    # machine health must be above zero and less than 5
    if 0 >= db["machine_health_arr"][machine_id]:
        return error_message("Machine id " + str(machine_id) + "'s health is too low")
    if db["machine_health_arr"][machine_id] >= 5:
        return error_message("Machine id " + str(machine_id) + "'s health is too high")

    if not db["assignments"]:
        db["assignments"] = [[player_id, machine_id]]
        return success_message()

    machine_already_assigned = False
    player_already_assigned = False
    for assignment in db["assignments"]:
        if assignment[0] == player_id:
            player_already_assigned = True
        if assignment[1] == machine_id:
            machine_already_assigned = True

    if machine_already_assigned:
        return error_message("machine_id already assigned")

    if player_already_assigned:
        return error_message("player_id already assigned")

    assig = db["assignments"]
    assig.append([player_id, machine_id])
    db["assignments"] = assig
    return success_message()


@application.route('/commander_generate_event', methods=['GET', 'POST'])
def gen_ev():
    if request.method == 'GET':
        return generate_event()
    else:
        return error_message("must use GET request")


def generate_event():
    """Randomly decrement the health (-=1) of a machine that has > 0 health."""

    db = shelve.open(DATABASE)
    check_if_everything_is_initialized()

    # increment counter
    db["counter"] += 1

    # randomly select a machine which has positive health, and decrement its health by 1
    health = db["machine_health_arr"]
    pos_health_machine_list = []
    for index in range(5):
        if health[index] > 0:
            pos_health_machine_list.append(index)

    if pos_health_machine_list:
        rand_choice = random.choice(pos_health_machine_list)
    else:
        return error_message("all machines are at health zero")

    health[rand_choice] -= 1
    db["machine_health_arr"] = health

    # check if game over
    tot = 0
    health_array = db["machine_health_arr"]
    for h in health_array:
        tot += h

    # check if lose
    if tot <= 0:
        db["session_status"] = "lose"

    # check if win
    if tot >= 25:
        db["session_status"] = "win"

    return success_message()


# ############## PLAYER ##################

@application.route('/player_set_task_result', methods=['GET', 'POST'])
def set_res():
    if request.method == 'POST':
        dat = request.get_json()
        if "machine_id" in dat and "result" in dat:
            return set_task_result(dat["machine_id"], dat["result"])
        else:
            return error_message("missing machine_id and or result")
    else:
        return error_message("must use POST request")


def set_task_result(machine_id, result):
    """POST the result (true or false) to the task_id on the server

    :param: task_id
    :param: result (True (success) / False (failure))

    """

    db = shelve.open(DATABASE)
    check_if_everything_is_initialized()

    # increment counter
    db["counter"] += 1

    # check to see if machine_id is in range
    if machine_id < 0 or machine_id > 4:
        return error_message("machine_id index out of range")

    # check to see if this is a valid request
    found = False
    found_id = -1
    for index, assignment in enumerate(db["assignments"]):
        if assignment[1] == machine_id:
            found = True
            found_id = index
    if not found:
        return error_message("this machine_id was not currently assigned as a task")

    # found! so remove it from the assignments dictionary
    assi = db["assignments"]
    del assi[found_id]
    db["assignments"] = assi

    # if success, increment health
    if result:
        # increment
        health = db["machine_health_arr"]
        if health[machine_id] < 5:
            health[machine_id] += 1
        db["machine_health_arr"] = health

    # check if game over
    tot = 0
    health_array = db["machine_health_arr"]
    for h in health_array:
        tot += h

    # check if lose
    if tot <= 0:
        db["session_status"] = "lose"

    # check if win
    if tot >= 25:
        db["session_status"] = "win"

    return success_message()


# ############## GENERAL UTILITIES ###################


def error_message(message):
    err = {"ERROR": message}
    return jsonify(err)


def success_message():
    msg = {"STATUS": "SUCCESS"}
    return jsonify(msg)


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
