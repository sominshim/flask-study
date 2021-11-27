# -*- coding: utf-8 -*-
from datetime import datetime, timedelta, date
from flask import Flask, render_template, flash, request, url_for, session
from werkzeug.utils import redirect
from flask_paginate import Pagination, get_page_parameter
from db_connect import db
from flask_migrate import Migrate
from models import Users, UserForm, PasswordForm, LoginForm, Rental, Book, Review
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_manager, login_user, LoginManager, login_required, logout_user, current_user
import babel
 
def format_datetime(value, format='yyyy-MM-dd'):
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
                session.get('login')
                flash("로그인 성공")
                return redirect(url_for('index'))
            else:
                flash("비밀번호가 틀렸습니다 - 다시 시도해주세요")
        else:
            flash("가입되지 않은 이메일입니다.")
    return render_template('login.html', form=form)

# 로그아웃
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    session.clear()
    flash("로그아웃되었습니다. 안녕히 가세요..")
    return redirect(url_for('login'))

# Create Dashboard Page
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    return render_template('dashboard.html')

# 대여 기록
@app.route('/returned_list')
@login_required
def returned_list():
    user_id = current_user.id
    rental = db.session.query(Book, Rental).filter(Book.id==Rental.book_id).\
                    filter(Rental.user_id==user_id, Rental.returned==1).order_by(Rental.return_date.desc())
    per_page = 8
    page = request.args.get('page', 1, type=int)
    pagination = rental.paginate(page,per_page,error_out=False)
    rental_list = pagination.items
    return render_template("rented_list.html",
                            rental_list= rental_list,
                            pagination=pagination,
                            enumerate = enumerate)

    # return render_template('rented_list.html', rental_list =rental_list)

@app.route('/rental_record/<int:id>')
@login_required
def rental_record(id):
    book = Book.query.filter(Book.id == id).first()

    # 책 재고가 없을 때
    if book.stock == 0:
        flash("재고가 없어 대출이 불가능합니다.")
        return render_template('index.html', book_list= Book.query.all())

    # 책 재고가 있을 때
    else:
        book.stock -= 1
        due_date=datetime.now()+timedelta(weeks=2)

        rental = Rental(
            returned = False, 
            rental_date=datetime.now(),
            due_date=due_date,
            user_id = current_user.id,
            book_id = book.id
            )
        db.session.add(rental)
        db.session.commit()
        flash("해당 도서를 대여하였습니다. 반납기한은 {}까지 입니다.".format(due_date.date()))
        return render_template('index.html', book_list= Book.query.all())

# 반납하기
@app.route('/book_return')
@login_required
def book_return():
    user_id = current_user.id
    rental = db.session.query(Book, Rental).filter(Book.id==Rental.book_id).\
                    filter(Rental.user_id==user_id, Rental.returned==0).order_by(Rental.rental_date.desc())
    per_page = 8
    page = request.args.get('page', 1, type=int)
    pagination = rental.paginate(page,per_page,error_out=False)
    rental_list = pagination.items

    return render_template("return_book.html",
                            rental_list= rental_list,
                            pagination=pagination,
                            enumerate = enumerate)


@app.route('/update_rental/<int:id>', methods=['POST', 'GET'])
def update_rental(id):
    user_id = current_user.id
    rental = Rental.query.filter_by(user_id=user_id, book_id=id, returned=0).first()
    rental.returned = 1
    rental.return_date = datetime.now()
    db.session.commit()

    book = Book.query.filter(Book.id == id).first()
    book.stock += 1

    db.session.commit()

    return redirect('/book_return')


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

# 회원가입
@app.route('/signup', methods=['GET', 'POST'])
def add_user():
    name = None
    form = UserForm()
    
    # 폼이 유효할 때
    if request.method == 'POST' and form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        # DB에 해당 유저가 없을 때
        if user is None:
            hashed_pw = generate_password_hash(form.password_hash.data, "sha256")
            user = Users(name=form.name.data, email=form.email.data, 
                        password_hash=hashed_pw)
            db.session.add(user)
            db.session.commit()
        else:
            flash("이미 가입된 아이디(이메일)입니다.")

        name = form.name.data
        flash("회원가입 되었습니다.")

    our_users = Users.query.order_by(Users.date_added)
    return render_template("add_user.html",
                            form = form,
                            name = name,
                            our_users=our_users)

# 메인 화면
@app.route('/')
def index():
    book = Book.query
    per_page = 8
    page = request.args.get('page', 1, type=int)
    pagination = book.paginate(page,per_page,error_out=False)
    book_list = pagination.items
    return render_template(
        "index.html",
        book_list= book_list,
        pagination=pagination,
        enumerate = enumerate
    )

# 책 소개 페이지
@app.route('/book_detail/<int:id>')
def book_detail(id):
    book = Book.query.filter(Book.id == id).first()
    reviews = ( 
        Review.query.filter(Review.book_id == book.id)
              .order_by(Review.created.desc()).all()
        )

    return render_template("book_detail.html",
                            book = book,
                            reviews = reviews)

# 책 리뷰
@app.route("/book_review/<int:id>", methods=['POST'])
@login_required
def book_review(id):
    action = request.form.get("act", type=str)

    if action == "write":
        # Review DB에 data추가
        content = request.form.get("content", type=str)
        score = request.form['score']

        review =Review(user_id = current_user.id, book_id= id, user_name = current_user.name, content = content, score=score, created=datetime.now())
        db.session.add(review)
        db.session.commit()

        # 평점 계산 후 Book DB에 score 업데이트
        review_list = Review.query.filter(Review.book_id==id).all()

        total_score = 0
        for review in review_list:
            total_score += review.score

        score = round((total_score / len(review_list)), 1)
        book = Book.query.filter(id==id).first()
        book.score = score
        
        db.session.commit()
        flash("댓글 작성 완료")

    return redirect('/book_detail/{}'.format(id))

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