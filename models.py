from db_connect import db
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError # 텍스트 입력.. 제출 등에 필요함
from wtforms.fields.simple import PasswordField
from wtforms.validators import DataRequired, EqualTo, Length # 유효성 검사
from werkzeug.security import generate_password_hash, check_password_hash

# Create Model
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(30), nullable=False, unique=True)
    favorite_color = db.Column(db.String(30))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    # Do some password stuff !!
    password_hash = db.Column(db.String(128))

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute !')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Create a String
    def __repr__(self):
        return '<Name %r>' % self.name

# Create a Form Class
class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    favorite_color = StringField("Favorite_Color")
    password_hash = PasswordField('Password', validators=[DataRequired(), EqualTo('password_hash2', message='Passwords Must Match!')])
    password_hash2 = PasswordField('Confirm Password', validators=[DataRequired()])
    submit =SubmitField("Submit")

# Create a PasswordForm Class
class PasswordForm(FlaskForm):
    email = StringField("What's Your Name", validators=[DataRequired()])
    password_hash = PasswordField("What's Your Password", validators=[DataRequired()])
    submit =SubmitField("Submit")

# Create a From Class
class NamerForm(FlaskForm):
    name = StringField("What's Your Name", validators=[DataRequired()])
    submit =SubmitField("Submit")
# learn more
# https://flask-wtf.readthedocs.io/en/1.0.x/