from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,FloatField,PasswordField
from wtforms.validators import InputRequired,NumberRange,Email,Length,EqualTo

class RegisterForm(FlaskForm):
    email=StringField("Email",validators=[InputRequired(),Email()])
    password=PasswordField("Password",validators=[InputRequired(),Length(min=4,message="Password must be at least 4 characters long.")])
    confirm_password=PasswordField("Confirm Password",validators=[InputRequired(),EqualTo("password",message="Passwords don't match.")])
    submit=SubmitField("Register")

class LoginForm(FlaskForm):
    email=StringField("Email",validators=[InputRequired(),Email()])
    password=PasswordField("Password",validators=[InputRequired()])
    submit=SubmitField("Login")

class AddTimetable(FlaskForm):
    name=StringField("Timetable Title",validators=[InputRequired()])
    submit=SubmitField("Add Timetable")

class AddSubject(FlaskForm):
    name=StringField("Subject",validators=[InputRequired()])
    duration=FloatField("Amount of time (Hours)",validators=[InputRequired(),NumberRange(min=0.1,max=5,message="Assignment should take between 0.1 and 5 hours")])
    submit=SubmitField("Add Subject")

