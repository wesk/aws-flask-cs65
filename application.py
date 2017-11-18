from flask import Flask
from flask import request

# ############## GAME SETUP ##################

def create_game():
    """Commander begins the game setup process with this command

    :return game_code
    """
    pass

def create_account():
    """POST

    Players create their accounts once the game code has been sent out

    :param game_code
    :param username

    :return: user_id
    """
    pass

def get_number_of_players():
    """Commander can see how many players have logged into the session so far

    :return: number_of_players
    """

def start_game():
    """POST? GET?

    Once all the players have created accounts, the commander can start the game"""
    pass


# ############## GENERAL ##################


def get_state():
    """

    :return: ship_health: (0 < ship_health <= 25)
    :return: array of machine healths (5x machines with health 5 = 25 health maximum)
    :return: array of machine assignments, ie what players are assigned to what machines
    """
    return "<h1>GAME STATUS</h1>\n"


# ############## COMMANDER ##################


def make_assignment():
    """POST

    :param: player_id
    :param: machine_id
    """
    pass


# ############## PLAYER ##################


def return_task_status():
    """POST

    :param: machine_id
    :param: True (success) / False (failure)

    """
    pass

# print a nice greeting.
def say_hello(username = "World"):
    return '<p>Hello %s!</p>\n' % username



def do_the_login():
    return "LOGGING IN -- POST"


def show_the_login_form():
    return "THIS IS THE LOGIN FORM -- GET"

# some bits of text for the page.
header_text = '''
    <html>\n<head> <title>CS65 Final Project Server</title> </head>\n<body>'''
instructions = '''
    <p><em>Hint</em>: This is a RESTful web service! Append a username
    to the URL (for example: <code>/Thelonious</code>) to say hello to
    someone specific.</p>\n'''
home_link = '<p><a href="/">Back</a></p>\n'
footer_text = '</body>\n</html>'

# EB looks for an 'application' callable by default.
application = Flask(__name__)

# add a rule for the index page.
application.add_url_rule('/', 'index', (lambda: header_text +
    say_hello() + instructions + footer_text))

# /status displays the ship status
application.add_url_rule('/state', "get_game_state", get_game_state)


@application.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return do_the_login()
    else:
        return show_the_login_form()

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
