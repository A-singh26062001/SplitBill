from email import message
from pyexpat.errors import messages
from flask import Flask,render_template,redirect,flash,url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager,UserMixin
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed,FileField
from requests import request
from wtforms import StringField,PasswordField,SubmitField,BooleanField
from wtforms.validators import DataRequired,Length,Email,EqualTo,ValidationError
from flask_bcrypt import Bcrypt
import bcrypt
from flask_login import login_user,current_user,logout_user,login_required
from flask_login import UserMixin
from flask_login import LoginManager
import sqlite3
from datetime import datetime

app=Flask(__name__)

#for login
login_manager=LoginManager(app)
login_manager.login_view='login'
login_manager.login_message_category='info'

#for database
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///users.db'
app.config['SECRET_KEY']='thisissecret'

db=SQLAlchemy(app)
bcrypt=Bcrypt(app)

# login_manager=LoginManager()
# login_manager.init_app(app)



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model,UserMixin):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(20),unique=True,nullable=False)
    email=db.Column(db.String(120),unique=True,nullable=False)
    password=db.Column(db.String(60),nullable=False)
    transactions=db.relationship('Transaction',backref='user')

    def __init__(self,username,email,password):
        self.username=username
        self.email=email
        self.password=password

class Transaction(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'))
    borrower_name=db.Column(db.String(200),nullable=False)
    amt=db.Column(db.Integer,nullable=True)
    desc=db.Column(db.String(200),nullable=False)
    date_created=db.Column(db.DateTime,default=datetime.utcnow)
    settlement=db.Column(db.Boolean,default=False,nullable=False)
    
    # def __init__(self,owner_name,borrower_name,amt,desc,settlement):
    #     self.owner_name=owner_name
    #     self.settlement=settlement
    #     self.borrower_name=borrower_name
    #     self.amt=amt
    #     self.desc=desc
    #     self.settlement=settlement




class RegistrationForm(FlaskForm):
    username=StringField('Enter Username', validators=[DataRequired(),Length(min=2,max=20)])
    email=StringField('Enter Email',validators=[DataRequired(),Email()])
    password=PasswordField('Enter Password',validators=[DataRequired()])
    confirm_password=PasswordField('Confirm Password',validators=[DataRequired(),EqualTo('password')])
    submit=SubmitField('Sign Up')

    def validate_username(self,username):

        user=User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose different one.')

    def validate_email(self,email):

        user=User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose different one.')

class LoginForm(FlaskForm):
    username=StringField('Enter Username',validators=[DataRequired(),Length(min=2,max=20)])
    password=PasswordField('Enter Password',validators=[DataRequired()])
    remember=BooleanField('Remember Me')
    submit=SubmitField('Login')


# @app.route('/')
# def login():
#     return render_template('login.html')

@app.route('/register',methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        users=User.query.all()
        # return redirect(url_for('home'),users=users)
    form=RegistrationForm()
    if form.validate_on_submit():
        hashed_pwd=bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user=User(username=form.username.data, email=form.email.data, password=hashed_pwd)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now logged in ','success')
        return redirect(url_for('login'))
    return render_template('regis.html',form=form)


@app.route('/',methods=['POST','GET'])
def login():
    if current_user.is_authenticated:
        return render_template('UserPage.html')
    form=LoginForm()
    if form.validate_on_submit():
        user=User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password,form.password.data):
            login_user(user,remember=form.remember.data)
            name=form.username.data
            allusers=User.query.filter(User.username!=current_user.username)
            return render_template('UserPage.html',allusers=allusers,name=name)
            # return redirect(url_for('home',users=users))
        else:
            flash("Login Unsuccessful. Please check the email and password")
    return  render_template('login.html',title='Login',form=form)
# @app.route('/UserPage')
# def home():
#     return render_template('UserPage.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__=='__main__':
    app.run(debug=True)
