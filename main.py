import os
from flask import Flask, render_template, request, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bootstrap import Bootstrap
from flask import Flask, render_template, jsonify
from random import sample
from flask_pymongo import PyMongo
import json
from bson import json_util

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
Bootstrap(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'thatsasecretkeyalright'
db = SQLAlchemy(app)


app.config['MONGO_URI'] = 'mongodb://localhost:27017/mydatabase'
mongo = PyMongo(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    
    def __repr__(self):
        return f"username: {self.username}\n password: {self.password}\n email: {self.email}"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class LoginForm(FlaskForm):
    username = StringField("Username:", validators=[DataRequired()])
    password = PasswordField("Password:", validators=[DataRequired()])

class SignUpForm(FlaskForm):
    username = StringField("Username:", validators=[DataRequired()])
    email = StringField("Email:", validators=[DataRequired(), Email(message="Not a Valid Email.")])
    password = PasswordField("Password:", validators=[DataRequired()])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():

    usersAll = User.query.all()

    formLogin = LoginForm()

    if formLogin.validate_on_submit():
        userExists = User.query.filter_by(username=formLogin.username.data).first()
        if userExists:
            if userExists.password == formLogin.password.data:
                login_user(userExists)
                return redirect(url_for('home_page'))
            
        #     return "<h1>Password does not match</h1>"
        # return "<h1> User does not exist</h1>"

    return render_template('login.html', formLogin= formLogin, users= usersAll)

@app.route('/signup', methods=['GET', 'POST'])
def sign_up():

    formSignUp = SignUpForm()

    if formSignUp.validate_on_submit():
        createUser = User(username= formSignUp.username.data, email= formSignUp.email.data, password= formSignUp.password.data)
        db.create_all()
        db.session.add(createUser)
        db.session.commit()
        return redirect(url_for('signed_up'))

    return render_template('signup.html', formSignUp= formSignUp)

@app.route('/signup-successful')
def signed_up():
    return render_template('signedUp.html')


@app.route('/home', methods=['GET', 'POST'])
@login_required
def home_page():
    return render_template('home.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return render_template('logout.html')


@app.route('/data')
def data():
    events = mongo.db.events
    results = events.find({})
    final_results = []
    for doc in results:
        final_result = json.dumps(doc, default=json_util.default)
        final_results.append(final_result)

    jsonified = jsonify(final_results)
    
    return jsonified

if __name__ == '__main__':
    app.run(debug=True)

