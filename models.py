from main import db

UserMatch = db.Table('UserMatch',
                     db.Column('uid', db.Integer, db.ForeignKey('User.id')),
                     db.Column('mid', db.Integer, db.ForeignKey('Match.id')))


class User(db.Model):
    __tablename__ = "User"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    email = db.Column(db.String(80))
    password = db.Column(db.String(80))
    is_admin = db.Column(db.Boolean)

    score = db.Column(db.Integer)
    num_white_win = db.Column(db.Integer)
    num_white_loss = db.Column(db.Integer)
    num_white_draw = db.Column(db.Integer)
    num_black_win = db.Column(db.Integer)
    num_black_loss = db.Column(db.Integer)
    num_black_draw = db.Column(db.Integer)

    matches = db.relationship('Match', secondary=UserMatch, back_populates='users')

    def __repr__(self):
        return self.name


class Match(db.Model):
    __tablename__ = "Match"

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    white = db.Column(db.Integer)
    white_won = db.Column(db.Boolean)

    users = db.relationship('User', secondary=UserMatch, back_populates='matches')

    def __repr__(self):
        return f"Match: {self.id}"
