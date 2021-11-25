from enum import unique
from flask import Flask, render_template, flash, request

from db_connect import db
from flask_migrate import Migrate
from models import Users, UserForm, PasswordForm, NamerForm
from werkzeug.security import generate_password_hash, check_password_hash

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

# Json Thing
@app.route('/date')
def get_current_date():
    favorite_pizza = {
        "John": "Peperoni",
        "Mary": "Cheese",
        "Tim": "Mushroom"
    }
    return favorite_pizza
    # return {"Date": date.today()}


@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.favorite_color = request.form['favorite_color']
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
                        favorite_color=form.favorite_color.data,
                        password_hash=hashed_pw)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ''
        form.email.data = ''
        form.favorite_color.data = ''
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

@app.route('/user/<name>')
def user(name):
    return render_template("user.html", user_name = name)

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

# Create name Page
@app.route('/name', methods=['GET', 'POST'])
def name():
    name = None
    form = NamerForm()
    # Validation Form
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
        flash("Form Submmitted Successfully!")

    return render_template("name.html",
        name = name,
        form = form)


if __name__ == "__main__":
    app.run(debug=True)