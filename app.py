from enum import unique
from flask import Flask, render_template, flash, request
from api import board

from db_connect import db
from flask_migrate import Migrate

# Create a Flask Instance
app = Flask(__name__)
app.register_blueprint(board)

# Add Database
# Old SQLite DB
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
# New MySQL DB
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://username:@password/db_name'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Shim5186!!@localhost/users'
# Secret Key
app.config['SECRET_KEY'] = "my super secret key that no one is supposed to know"
# Initialize the DB
db.init_app(app)
migrate = Migrate(app, db)


if __name__ == "__main__":
    app.run(debug=True)
