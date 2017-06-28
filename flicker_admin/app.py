from flask import Flask
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)


def setup_admin(Base, *models):
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
    db = SQLAlchemy(app)

    Base.metadata.create_all(db.engine)

    admin = Admin(app, name='flicker_admin', template_mode='bootstrap3', url='/')
    for model in models:
        admin.add_view(ModelView(model, db.session))

