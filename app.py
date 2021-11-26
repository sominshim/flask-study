from enum import unique
from flask import Flask, render_template, flash, request, url_for
from werkzeug.utils import redirect
from wtforms.fields.simple import StringField, SubmitField
from wtforms.validators import DataRequired

from db_connect import db
from flask_migrate import Migrate
from models import Users, UserForm, PasswordForm, NamerForm, LoginForm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_manager, login_user, LoginManager, login_required, logout_user, current_user

# Create a Flask Instance
app = Flask(__name__)

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
                flash("Login Successfull !")
                return redirect(url_for('dashboard'))
            else:
                flash("Wrong Password - Try Again!")
        else:
            flash("That User Doesn't Exist! Try Again...")
    return render_template('login.html', form=form)

# Creat Logout Page
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash("Your Have Been Logged Out! Thanks For Stopping By...")
    return redirect(url_for('login'))

# Create Dashboard Page
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
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

        flash("User Added Successfully!")
    our_users = Users.query.order_by(Users.date_added)

    return render_template("add_user.html",
        form = form,
        name = name,
        our_users=our_users)


@app.route('/')
def index():
    first_name = "John"
    return render_template("index.html", first_name = first_name)

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