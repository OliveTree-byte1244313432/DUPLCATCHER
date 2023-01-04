from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import SelectMultipleField
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember me')
    submit = SubmitField('Login')

class AddPaper(FlaskForm):
    paper = FileField('Paper', validators=[FileAllowed(['pages', 'docx', 'doc', 'pdf', 'txt', 'odt', 'png', 'jpg', 'jpeg']), DataRequired()])
    language = SelectMultipleField('Programming Language', choices=[('english', 'English'),('french', 'French'),('spanish', 'Spanish')], validators=[DataRequired()])
    time = FileField('time', validators=[DataRequired()])
    submit = SubmitField('Submit')
