"""Chess Site for Chess Club"""

from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template
from sqlalchemy import insert, true, update, delete


app = Flask(__name__)

# get path of database as path to this folder then to file
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///chess.db"
# app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


from models import *


def winrate(user):
    """Calculates and returns the total, white and black winrates in a list"""

    not_wins = user.num_white_loss + user.num_white_draw + user.num_black_loss + user.num_black_draw
    total_winrate = 0 if not_wins <= 0 else (user.num_white_win + user.num_black_win) / not_wins

    not_white_wins = (user.num_white_loss + user.num_white_draw)
    white_winrate = 0 if not_white_wins <= 0 else user.num_white_win / not_white_wins

    not_black_wins = (user.num_black_loss + user.num_black_draw)
    black_winrate = 0 if not_black_wins <= 0 else user.num_black_win / not_black_wins

    return [total_winrate, white_winrate, black_winrate]


@app.route('/')
def leaderboard():
    """Shows the leaderboard of a group"""

    # get players => [score, name, overall winrate, white winrate, black winrate]
    # sorted from highest score to lowest
    players = [[user.score, user.name] + winrate(user) for user in User.query.all()]
    players.sort(reverse=True)

    return render_template("leaderboard.html", title="Leaderboard", players=players)


def matches():
    """Shows the previous matches"""
    return


if __name__ == "__main__":

    players = [[user.score, user.name] + winrate(user) for user in User.query.all()]
    players.sort(reverse=True)
    print(players)

    # new_match = Match(id=1, white=1, white_won=True)

    # db.session.add(new_match)
    # # db.session.add(new_match)
    # # db.session.add(new_match)
    # db.session.commit()

    app.run(debug=True)
