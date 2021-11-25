from flask import Flask, render_template, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField # 텍스트 입력.. 제출 등에 필요함
from wtforms.validators import DataRequired # 유효성 검사

# Create a Flask Instance
app = Flask(__name__)
app.config['SECRET_KEY'] = "my super secret key that no one is supposed to know"

# Create a From Class
class NamerForm(FlaskForm):
    name = StringField("What's Your Name", validators=[DataRequired()])
    submit =SubmitField("Submit")
# learn more
# https://flask-wtf.readthedocs.io/en/1.0.x/

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
