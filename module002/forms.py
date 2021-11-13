from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, DateTimeField, SelectField, HiddenField, TextAreaField
from wtforms.validators import InputRequired, Length
from wtforms.fields.html5 import DateField, TimeField, DateTimeLocalField
import datetime


class CommentForm(FlaskForm): # class RegisterForm extends FlaskForm
    comment = TextAreaField('Write your comment', validators=[Length(max=3000), InputRequired()])