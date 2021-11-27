from db_connect import db
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, EmailField, ValidationError # 텍스트 입력.. 제출 등에 필요함
from wtforms.fields.simple import PasswordField
from wtforms.validators import DataRequired, EqualTo, Length # 유효성 검사
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user


class Rental(db.Model):
    __tablename__ = 'rental'

    id = db.Column(db.Integer, nullable=False, primary_key=True, autoincrement=True)
    returned = db.Column(db.Boolean, nullable=False, default=False)
    rental_date = db.Column(db.DateTime)
    return_date = db.Column(db.DateTime, nullable=True)
    due_date = db.Column(db.DateTime)
    book_id = db.Column(db.Integer, db.ForeignKey("book.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)


    def __init__(self, returned, rental_date, due_date, book_id, user_id):
        self.returned = returned
        self.rental_date = rental_date
        self.due_date = due_date
        self.book_id = book_id
        self.user_id = user_id

class Review(db.Model):
    __tablename__ = "review"

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    score = db.Column(db.Integer, nullable=False)
    created = db.Column(db.DateTime)
    book_id = db.Column(db.Integer, db.ForeignKey("book.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    user_name = db.Column(db.String(30), default="", nullable=True)

    def __init__(self, user_id, book_id, user_name, content, score, created):
        self.content = content
        self.score = score
        self.book_id = book_id
        self.user_id = user_id
        self.user_name = user_name
        self.created = created


# Create Model
class Users(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(30), nullable=False, unique=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    # Do some password stuff !!
    password_hash = db.Column(db.String(128))
    rental = db.relationship(Rental, backref="users")
    review = db.relationship(Review, backref="users")


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
    name = StringField("이름", validators=[DataRequired(), Length(min=3, max=25)])
    email = EmailField("이메일", validators=[DataRequired()])
    password_hash = PasswordField('비밀번호', validators=[DataRequired(), EqualTo('password_hash2', message='비밀번호가 일치하지 않습니다')])
    password_hash2 = PasswordField('비밀번호 확인', validators=[DataRequired()])
    submit =SubmitField("가입")

# Create a PasswordForm Class
class PasswordForm(FlaskForm):
    email = StringField("What's Your Name", validators=[DataRequired()])
    password_hash = PasswordField("What's Your Password", validators=[DataRequired()])
    submit =SubmitField("Submit")

class LoginForm(FlaskForm):
    email = EmailField("이메일", validators=[DataRequired()])
    password = PasswordField("비밀번호", validators=[DataRequired()])
    submit = SubmitField("로그인")
    
# learn more
# https://flask-wtf.readthedocs.io/en/1.0.x/

class Book(db.Model):
    __tablename__ = 'book'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    book_name = db.Column(db.String(100), nullable=False, unique=True)
    publisher = db.Column(db.String(50), nullable=False)
    author = db.Column(db.String(50), nullable=False)
    publication_date = db.Column(db.Date)
    pages = db.Column(db.Integer, nullable=False)
    isbn = db.Column(db.BigInteger, nullable=False)
    descrip = db.Column(db.TEXT, nullable=False)
    link = db.Column(db.String(500), nullable=False)
    img_path = db.Column(db.String(500), nullable=False)
    stock = db.Column(db.Integer, default=5)
    score = db.Column(db.Integer, default=0)

    rental = db.relationship(Rental, backref="book")
    review = db.relationship(Review, backref="book")


    def __init__(self,id,book_name,publisher,author,publication_date,pages,isbn,descrip,link,img_path,stock,score):
        self.id = id
        self.book_name = book_name
        self.publisher = publisher
        self.author = author
        self.publication_date = publication_date
        self.pages = pages
        self.isbn = isbn
        self.descrip = descrip
        self.link = link
        self.img_path = img_path
        self.stock = stock
        self.score = score
        
