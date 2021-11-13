from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, DateTimeField, SelectField, HiddenField#, DateField
from wtforms.validators import InputRequired, Length
from wtforms.fields.html5 import DateField, TimeField, DateTimeLocalField
import datetime

class FollowForm(FlaskForm): # class RegisterForm extends FlaskForm
    code = StringField('Enter the course code you wish to follow / unfollow:',validators=[InputRequired(),Length(min=1,max=50)])

class CourseForm(FlaskForm): # class RegisterForm extends FlaskForm
    id = StringField('id')
    name = StringField('Course Name',validators=[InputRequired(),Length(min=1,max=50)])
    institution_name = StringField('Institution Name')
    code = StringField('Course Code')

class ParticipationCodeForm(FlaskForm): # class RegisterForm extends FlaskForm
    id = StringField('id')
    course_id = SelectField('Course', choices = [], validators = [InputRequired()])
    activity_name = StringField('Título',validators=[Length(max=100)])
    activity_description = StringField('Descripción',validators=[Length(max=1000)])
    date_expire = DateField('Choose an expiring date',format='%Y-%m-%d', default=datetime.datetime.today)
    time_expire = TimeField('Expiring time',format='%H:%M', default=datetime.time(23, 59))

class EntregaForm(FlaskForm): # class RegisterForm extends FlaskForm
    content = StringField('Descripción',validators=[Length(max=10000)])
    nota = StringField('Nota', default="Sin definir")
