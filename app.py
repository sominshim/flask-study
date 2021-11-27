from enum import unique
from flask import Flask, render_template, flash, request, url_for, jsonify
from werkzeug.utils import redirect
from wtforms.fields.simple import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_paginate import Pagination, get_page_parameter
from db_connect import db
from flask_migrate import Migrate
from models import Users, UserForm, PasswordForm, LoginForm, Rental, Book, Review
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_manager, login_user, LoginManager, login_required, logout_user, current_user
from sqlalchemy.sql import func
from sqlalchemy import asc, desc
import babel
 
def format_datetime(value, format='yyyy-MM-dd HH:mm:ss'):
    return babel.dates.format_datetime(value, format)
 

# Create a Flask Instance
app = Flask(__name__)
app.jinja_env.filters['datetime'] = format_datetime
# Add Database
# New MySQL DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Shim5186!!@localhost/users'
app.config['SECRET_KEY'] = "my super secret key that no one is supposed to know"

# Initialize the DB
db.init_app(app)
migrate = Migrate(app, db)

with app.app_context():
    db.create_all()
# Flask_Login Stuff
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

# Create Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user:
            # check hash
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                flash("로그인 성공")
                return redirect(url_for('index'))
            else:
                flash("비밀번호가 틀렸습니다 - 다시 시도해주세요")
        else:
            flash("가입되지 않은 이메일입니다.")
    return render_template('login.html', form=form)

# Creat Logout Page
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash("로그아웃되었습니다. 안녕히 가세요..")
    return redirect(url_for('login'))

# Create Dashboard Page
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    return render_template('dashboard.html')

# 대여기록
@app.route('/rental_record')
def rental_record():
    return render_template('dashboard.html')


# 반납하기
@app.route('/book_return')
def book_return():
    return render_template('dashboard.html')


@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        
        try:
            db.session.commit()
            flash("User Updated Successfully!")
            return render_template("update.html", 
                form=form,
                name_to_update= name_to_update)
        except:
            flash("Error! Looks like there was a problem... try again")
            return render_template("update.html", 
                form=form,
                name_to_update= name_to_update)
    else:
        return render_template("update.html", 
            form=form,
            name_to_update= name_to_update,
            id=id)

@app.route('/delete/<int:id>')
def delete(id):
    user_to_delete = Users.query.get_or_404(id)
    name = None
    form = UserForm()

    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash("User Deleted Successfully!")

        our_users = Users.query.order_by(Users.date_added)
        return render_template("add_user.html",
            form = form,
            name = name,
            our_users=our_users)
    except:
        flash("Whoops! There was a problem deleting user, try again...")
        return render_template("add_user.html",
            form = form,
            name = name,
            our_users=our_users)


@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
    name = None
    form = UserForm()

    # Validation Form
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            # Hash the password !!
            hashed_pw = generate_password_hash(form.password_hash.data, "sha256")
            user = Users(name=form.name.data, email=form.email.data, 
                        password_hash=hashed_pw)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ''
        form.email.data = ''
        form.password_hash.data = ''

        flash("회원 가입 되었습니다.")
    our_users = Users.query.order_by(Users.date_added)

    return render_template("add_user.html",
        form = form,
        name = name,
        our_users=our_users)

@app.route('/')
def index():
    return render_template(
        "index.html",
        book_list= Book.query.all()
    )

@app.route('/book_detail/<int:id>')
def book_detail(id):
    book = Book.query.filter(Book.id == id).first()
    reviews = ( 
        Review.query.filter(Review.book_id == book.id)
              .order_by(desc(Review.created)).all()
        )

    return render_template(
        "book_detail.html",
        book = book,
        reviews = reviews
    )

@app.route("/book_review/<int:id>", methods=['GET', 'POST'])
def book_review(id):
    action = request.form.get("act", type=str)

    if action == "write":
        content = request.form.get("content", type=str)
        score = request.form['score']

        review =Review(user_id = current_user.id, book_id= id, user_name = current_user.name, content = content, score=score)
        db.session.add(review)
        db.session.commit()

    return redirect('/book_detail/<int:id>')

# Create Custom Error Pages
# Invalid URL
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

# Internal Server Error
@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html"), 500

# Create Password Test Page
@app.route('/test_pw', methods=['GET', 'POST'])
def test_pw():
	email = None
	password = None
	pw_to_check = None
	passed = None
	form = PasswordForm()

	# Validate Form
	if form.validate_on_submit():
		email = form.email.data
		password = form.password_hash.data
		# Clear the form
		form.email.data = ''
		form.password_hash.data = ''

		# Lookup User By Email Address
		pw_to_check = Users.query.filter_by(email=email).first()
		
		# Check Hashed Password
		passed = check_password_hash(pw_to_check.password_hash, password)

	return render_template("test_pw.html", 
		email = email,
		password = password,
		pw_to_check = pw_to_check,
		passed = passed,
		form = form)

if __name__ == "__main__":
    app.run(debug=True)