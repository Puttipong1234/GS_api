from flask_sqlalchemy import SQLAlchemy

from Project import app


db = SQLAlchemy(app)

class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session = db.Column(db.String(80),unique = True)

    def __init__(self,session):
        self.session = session


    