"""Chess Site for Chess Club"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, redirect, request


app = Flask(__name__)

# get path of database as path to this folder then to file
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///chess.db"
# app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

from models import *


def winrate(user):
    """Calculates and returns the total, white and black winrates in a list"""

    not_wins = user.num_white_loss + user.num_white_draw + user.num_black_loss + user.num_black_draw
    wins = user.num_white_win + user.num_black_win
    if wins + not_wins <= 0:
        # haven't played a game yet
        return [0, 0, 0]

    if not_wins == 0:
        total_winrate = 100
    else:
        total_winrate = wins / (wins + not_wins) * 100

    not_white_wins = user.num_white_loss + user.num_white_draw
    if not_white_wins + user.num_white_win == 0:
        white_winrate = 0
    else:
        if not_white_wins == 0:
            white_winrate = 100
        else:
            white_winrate = user.num_white_win / (user.num_white_win + not_white_wins) * 100

    not_black_wins = user.num_black_loss + user.num_black_draw
    if not_black_wins + user.num_black_win == 0:
        black_winrate = 0
    else:
        if not_black_wins == 0:
            black_winrate = 100
        else:
            black_winrate = user.num_black_win / (user.num_black_win + not_black_wins) * 100

    return [round(total_winrate, 1), round(white_winrate, 1), round(black_winrate, 1)]


def change_winrate(user, is_white, did_win, score_difference):
    """Calculates new winrate for User"""
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

    # print(user.score, score_multiplier, expectedScore, value, score_difference)
    # print(new_score, is_white, did_win)

    user.score = new_score

    return user


def sort_by_date(match):
    """returns the key for sorting by date"""
    date = list(map(int, match[0].split("-")))

    return [-date[2], -date[1], -date[0]]


@app.route("/")
def main():
    return redirect("/leaderboard")



@app.route('/leaderboard', methods=["GET"])
def leaderboard():
    """Shows the leaderboard of a group"""

    # get players => [score, name, overall winrate, white winrate, black winrate]
    # sorted from highest score to lowest
    players = [[user.score, user.name] + winrate(user) for user in User.query.all()]
    players.sort(reverse=True)

    return render_template("leaderboard.html", title="Leaderboard", players=players)


@app.route('/matches', methods=["GET"])
def matches():
    """Shows the previous matches"""

    match_list = Match.query.all()
    match_list = [[match.date.strftime("%d-%m-%Y"),
                   [[user.id, user.name] for user in match.users],
                   match.white, match.white_won] for match in match_list]
    match_list.sort(key=sort_by_date)

    if len(match_list) == 0:
        return render_template("matches.html", matches=[])

    timed_list = [[match_list[0][0], []]]
    for match in match_list:
        date = match[0]

        winner = "Draw"

        if match[2] == match[1][0][0]:
            white = match[1][0][1]
            black = match[1][1][1]
        else:
            white = match[1][1][1]
            black = match[1][0][1]

        if match[3] == 1:
            # white won
            winner = white[:]
        elif match[3] == 0:
            # black wins
            winner = black[:]

        # print(winner)

        match = [match[1][0][1], match[1][1][1], winner]

        # print(match[2])

        if date == timed_list[-1][0]:
            # same date
            timed_list[-1][1].append(match)
        else:
            timed_list.append([date, [match]])

    # for day, matchlist in timed_list:
    #     print(f"{day}:")
    #     for white, black, winner in matchlist:
    #         print(f"{white:10}{black:10}{winner:10}")
    
    # print("\n\n", timed_list)

    return render_template("matches.html", matches=timed_list)


@app.route("/autofill_matches", methods=["POST"])
def autofill_matches():
    """returns all players where names are similar for autofill purposes"""
    # print("Try")
    data = request.form.get("data")

    # print(data)

    info = [(user.id, user.name) for user in
            User.query.filter(User.name.like(data + "%")).all()]
    info += [(user.id, user.name) for user in
             User.query.filter(User.name.like("%" + data + "%")).all()]

    players = []

    for player in info:
        if player not in players:
            players.append(player)

    players = list(map(str, players))

    # print("|".join(players))

    return "|".join(players)


@app.route('/add_match', methods=["GET"])
def add_match():
    """add a new match"""

    players = [user.name for user in User.query.all()]
    players.sort()

    return render_template("add_match.html", title="Add Match", players=players)


@app.route('/new_match', methods=["POST"])
def new_match():
    """add new match to database"""
    white, black, winner = \
        [request.form.get("white"), request.form.get("black"), request.form.get("winner")]

    winner = float(winner)
    if winner == -1:
        return "no winner"

    white = User.query.filter_by(name=white).first_or_404()
    black = User.query.filter_by(name=black).first_or_404()

    if white.id == black.id:
        return "same person"

    new_match = Match(date=datetime.date(datetime.now()), white=white.id, white_won=winner)
    new_match.users.append(white)
    new_match.users.append(black)

    db.session.add(new_match)

    scores = [white.score, black.score]

    white = change_winrate(white, True, winner, scores[1] - scores[0])
    black = change_winrate(black, False, 1 - winner, scores[0] - scores[1])

    db.session.commit()

    return redirect("/matches")

@app.route("/login_page")
def login_page():
    return render_template("login.html")

if __name__ == "__main__":
    app.run(debug=True)
