from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, PasswordField, SelectField
from wtforms.validators import InputRequired, Length, Email, DataRequired, Regexp, EqualTo
from wtforms.fields.html5 import EmailField
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.file import FileField, FileRequired, FileAllowed


class connectForm(FlaskForm):
    email = EmailField('Email of your friend', validators=[InputRequired(), Email()])
    submit = SubmitField('submit')

class uploadForm(FlaskForm):
   # photo = FileField(validators=[FileAllowed(photos, 'Image only!'), FileRequired('File was empty!')])
    foodImage = FileField('foodImage', validators=[FileRequired(), FileAllowed(['jpg', 'png'], 'Images only!')])
    message = TextAreaField('Message', validators=[InputRequired()], render_kw={'rows': 2})
    submit = SubmitField('Upload my food')


class ContactForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired(), Length(min=2, max=15)])
    email = EmailField('Email', validators=[InputRequired(), Email()])
    message = TextAreaField('Message', validators=[InputRequired()], render_kw={'rows': 2})
    submit = SubmitField('SEND MESSAGE')


class ReviewForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired(), Length(min=2, max=15)])
    message = TextAreaField('Customer review', validators=[InputRequired()], render_kw={'rows': 7})
    rate = SelectField('rating', choices=[('one', '1'), ('two', '2'), ('three', '3'), ('four', '4'), ('five', '5')])
    submit = SubmitField('Send Review')


class LoginForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    submit = SubmitField('login')


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(4, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                                                              'Usernames must start with a letter and must have only letters, numbers, dots or underscores')])
    email = EmailField('Email', validators=[InputRequired(), Email()])
    phone = StringField('Phone number', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired(), Length(8)])
    password2 = PasswordField('Repeat password',
                              validators=[InputRequired(), EqualTo('password', message='Passwords must match.')])
    submit = SubmitField('submit')


class forgotpwForm(FlaskForm):
    email = EmailField('Email', validators=[InputRequired(), Email()])
    submit = SubmitField('submit')



class changeMyPasswordForm(FlaskForm):
    email = EmailField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('New Password', validators=[InputRequired(), Length(8)])
    password2 = PasswordField('Repeat password',
                              validators=[InputRequired(), EqualTo('password', message='Passwords must match.')])
    submit = SubmitField('submit')
