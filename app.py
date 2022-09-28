"""Chess Site for Chess Club"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, redirect, request, session
from random import choice


app = Flask(__name__)

# get path of database as path to this folder then to file
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///chess.db"
# app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = "b'\x10M\xe2\n\xa4\x95Q\x83\x7f\x062\xde`\x9f:\x15\x16\x18\\:,x\n\tJ\xa0+\x18\x08X3\xf4i;\xc8F\xd7\x0bu'"

from models import *


ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


def better_round(num, dp=1):
    """returns a rounded number to a float if it rounds to the decimal places
    or a whole number if it rounds to that"""
    if int(num) != round(num, dp):
        return round(num, dp)
    else:
        return int(num)


def generate_salt(size=16):
    """creates a random string of length size for use as a salt for password hashing"""
    return "".join([choice(ALPHABET) for _ in range(size)])


@app.route("/get_error", methods=["POST"])
def get_error():
    """returns the error that occured or nothing if no error"""
    if 'error' in session:
        errors = session['error']
        del session['error']
        txt = " - " + "\n - ".join(errors)
        return txt
    else:
        return ''


def set_error(txt=''):
    """sets a current error"""
    if 'error' in session and txt not in session['error']:
        session['error'].append(txt)
    else:
        session['error'] = [txt]


def winrate(user):
    """Calculates and returns the total, white and black winrates in a list"""

    not_wins = user.num_white_loss + user.num_white_draw + user.num_black_loss + user.num_black_draw
    wins = user.num_white_win + user.num_black_win
    if wins + not_wins <= 0:
        # haven't played a game yet
        return [0, 0, 0]

    total_winrate = wins / (wins + not_wins) * 100

    # calculate white winrate
    not_white_wins = user.num_white_loss + user.num_white_draw
    if not_white_wins + user.num_white_win == 0:
        white_winrate = 0
    else:
        if not_white_wins == 0:
            white_winrate = 100
        else:
            white_winrate = user.num_white_win / (user.num_white_win + not_white_wins) * 100

    # calculate black winrate
    not_black_wins = user.num_black_loss + user.num_black_draw
    if not_black_wins + user.num_black_win == 0:
        black_winrate = 0
    else:
        if not_black_wins == 0:
            black_winrate = 100
        else:
            black_winrate = user.num_black_win / (user.num_black_win + not_black_wins) * 100

    # return winrates in a list
    # [overall winrate, white winrate, black winrate]
    return [better_round(total_winrate), better_round(white_winrate), better_round(black_winrate)]


def change_winrate(user, is_white, did_win, score_difference):
    """Calculates new winrate for User given a round that happened"""
    if did_win == 0.5:
        # draw
        if is_white:
            user.num_white_draw += 1
        else:
            user.num_black_draw += 1
    elif is_white:
        if did_win == 1:
            user.num_white_win += 1
        else:
            user.num_white_loss += 1
    else:
        if did_win == 1:
            user.num_black_win += 1
        else:
            user.num_black_loss += 1

    games_played = user.num_white_win + user.num_white_loss + user.num_white_draw \
        + user.num_black_win + user.num_black_loss + user.num_black_draw

    # elo calculation
    score_multiplier = max(10, min(400, int(400 / games_played)))  # keep multiplier between 10 and 400
    ratio = score_difference / 400
    value = 10**ratio + 1
    expectedScore = 1 / value

    new_score = round(user.score + score_multiplier * (did_win - expectedScore))

    user.score = new_score

    return user


def get_current_user():
    """get the id of the current user"""
    if 'userid' in session:
        # get user
        return session['userid']
    else:
        return None

@app.route("/get_user", methods=["POST"])
def get_current_user_name():
    """get the name of the current user"""
    user = get_current_user()
    if user is None:
        return ""
    user = User.query.filter_by(id=user).all()
    if len(user) == 0:
        set_error("user does not exist")
        return ""
    else:
        return user[0].name


def hash(word, salt=""):
    """returns the hash of a password and salt"""
    word = int("".join([str(ord(letter)) for letter in str(word) + str(salt)]))
    word *= word * word * 45328249863
    new_word = word % 3285734698327
    new_word *= ((word % 1287359) * 982347) % 92589837
    return str(new_word)


def sort_by_date(match):
    """returns the key for sorting by date"""
    date = list(map(int, match[0].split("-")))

    return [-date[2], -date[1], -date[0]]


@app.route("/")
def main():
    """takes user to main page"""
    return redirect("/leaderboard")


@app.route('/leaderboard', methods=["GET"])
def leaderboard():
    """Shows the leaderboard of a group"""

    users = User.query.all()
    # get players => [score, name, overall winrate, white winrate, black winrate]
    players = [[user.score, user.name] + winrate(user) for user in users]
    # order by highest
    players.sort(reverse=True)

    return render_template("leaderboard.html", title="Leaderboard", players=players)


@app.route('/matches', methods=["GET"])
def matches():
    """Shows the previous matches"""

    # get matches and sort by newest
    match_list = Match.query.all()
    match_list = [[match.date.strftime("%d-%m-%Y"),
                   [[user.id, user.name] for user in match.users],
                   match.white, match.white_won] for match in match_list] 
    match_list.sort(key=sort_by_date)

    if len(match_list) == 0:
        return render_template("matches.html", matches=[])

    # matches are to be seperated by day -> loop through matches and put into a different list
    #                                       if different day
    timed_list = [[match_list[0][0], []]]
    for match in match_list:
        date = match[0]

        winner = "Draw"

        # get the white and black player
        if match[2] == match[1][0][0]:
            white = match[1][0][1]
            black = match[1][1][1]
        else:
            white = match[1][1][1]
            black = match[1][0][1]

        # get winner
        if match[3] == 1:
            # white won
            winner = white[:]
        elif match[3] == 0:
            # black wins
            winner = black[:]

        match = [match[1][0][1], match[1][1][1], winner]

        if date == timed_list[-1][0]:
            # same date
            timed_list[-1][1].append(match)
        else:
            timed_list.append([date, [match]])

    return render_template("matches.html", matches=timed_list)


@app.route("/autofill_matches", methods=["POST"])
def autofill_matches():
    """returns all players where names are similar for autofill purposes"""
    data = request.form.get("data")

    # get all users that contains the letters given
    info = [(user.id, user.name) for user in
            User.query.filter(User.name.like(data + "%")).all()]
    info += [(user.id, user.name) for user in
             User.query.filter(User.name.like("%" + data + "%")).all()]

    players = []

    # remove copies
    for player in info:
        if player not in players:
            players.append(player)

    players = list(map(str, players))

    return "|".join(players)


@app.route('/new_match', methods=["GET","POST"])
def new_match():
    """add new match to database"""

    if request.method == "POST":
        if get_current_user() is None:
            set_error("you muct be logged in to use this feature")
            return redirect("/new_match")

        white, black, winner = \
            [request.form.get("white"), request.form.get("black"), request.form.get("winner")]

        white = User.query.filter_by(id=white).first() # popup error if player does not exist
        black = User.query.filter_by(id=black).first()

        # check if players and winner exists
        if white is None:
            set_error("white player does not exist")
        if black is None:
            set_error("black player does not exist")

        if 'error' in session:
            return "" # if there is an error return back to the page

        winner = float(winner) # winner is 0 for black, 1 for white and 0.5 for draw
        if winner == -1:
            set_error("no winner")

        if white == black:
            set_error("same person")
        
        if 'error' in session:
            return ""

        # create match
        match = Match(date=datetime.date(datetime.now()), white=white.id, white_won=winner)
        match.users.append(white)
        match.users.append(black)

        db.session.add(match)

        scores = [white.score, black.score]

        # update winrates for both players
        white = change_winrate(white, True, winner, scores[1] - scores[0])
        black = change_winrate(black, False, 1 - winner, scores[0] - scores[1])

        db.session.commit()

        return redirect("/matches")
    else:
        # get all players that can be put into a match
        players = [user.name for user in User.query.all()]
        players.sort()

        if get_current_user() is None:
            set_error("you must be logged in to use this feature")
            return render_template("add_match.html", title="Add Match", players=players, has_user=False)

        return render_template("add_match.html", title="Add Match", players=players, has_user=True)


@app.route("/login", methods=["GET", "POST"])
def login():
    """login page and login method which checks if the user provided the correct details to login"""
    if request.method == "POST":
        username, password = [request.form.get("username"), request.form.get("password")]
        user = User.query.filter_by(name=username).all()
        if len(user) == 0 or str(hash(password, user[0].salt)) != str(user[0].password):
            set_error("invalid details")
            return redirect("/login")
        user = user[0]

        session["userid"] = user.id

        return redirect("/leaderboard")

    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    """signup page and signup method which takes in a username and a password along 
    with a test check password"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirm_password = request.form.get("password confirm")

        for user in User.query.all():
            if username.lower() == user.name.lower():
                set_error("username already exists")
                return redirect("/signup")

        if username == "":
            set_error("username cannot be empty")
        elif username in ["Draw"]:
            set_error("username is invalid=")
        elif len(username) > 30:
            set_error("username is too long. please keep username 30 characters or less")
        if password == "":
            set_error("password cannot be empty")
        if "error" in session:
            return redirect("/signup")
        if password != confirm_password:
            set_error("passwords do not match")
            return redirect("/signup")

        # hash password
        salt = generate_salt()
        password = hash(password, salt)

        new_user = User(
            name=username,
            password=password,
            salt=salt,
            is_admin=False,
            score=1500,

            num_white_win=0,
            num_white_loss=0,
            num_white_draw=0,
            num_black_win=0,
            num_black_loss=0,
            num_black_draw=0
        )

        db.session.add(new_user)
        db.session.commit()

        session["userid"] = new_user.id

        return redirect("/")
    return render_template("signup.html")


@app.route("/logout", methods=["GET"])
def logout():
    """logout user"""
    if "userid" in session:
        del session["userid"]
        return redirect("/")
    else:
        set_error("Not signed in")
        return redirect("/")


@app.errorhandler(404)
def page_not_found_error(e):
    """page not found page"""
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    """internal server error page"""
    # note that we set the 500 status explicitly
    return render_template('500.html'), 500


if __name__ == "__main__":
    app.run(debug=True)
