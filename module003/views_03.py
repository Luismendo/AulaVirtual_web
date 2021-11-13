from flask import Blueprint, render_template, abort, flash, redirect, url_for, request, send_file
from flask_login import login_required, current_user
from sqlalchemy import or_, and_
from models import get_db, User, Course, ParticipationCode, ParticipationRedeem, Actividad,Follow, Entregas, Nota
from flask_uploads import configure_uploads, IMAGES, UploadSet
from werkzeug.utils import secure_filename
import random
import os
from application import get_app
import datetime

app = get_app()

from module003.forms import *

module003 = Blueprint("module003", __name__,static_folder="static",template_folder="templates")
db = get_db()

app.config['UPLOADED_IMAGES_DEST'] = '/home/Luismen/uploads'
app.config["ALLOWED_IMAGE_EXTENSIONS"] = ["JPEG", "JPG", "PNG", "GIF","TXT","PDF","ZIP","RAR"]
app.config["MAX_IMAGE_FILESIZE"] = 0.5 * 1024 * 1024

####
images = UploadSet('images', IMAGES)
configure_uploads(app, images)

def allowed_file(filename):

    if not "." in filename:
        return False

    ext = filename.rsplit(".", 1)[1]

    if ext.upper() in app.config["ALLOWED_IMAGE_EXTENSIONS"]:
        return True
    else:
        return False


def allowed_image_filesize(filesize):

    if int(filesize) <= app.config["MAX_IMAGE_FILESIZE"]:
        return True
    else:
        return False
#####

@module003.route('/',methods=['GET','POST'])
@login_required
def module003_participation_generate():
    form = ParticipationCodeForm()
    if request.method == 'POST':
        try:
            course = Course.query.get(form.course_id.data)
            if course.user_id is not current_user.id:
                flash("You don't have access to the course")
                return redirect(url_for('module003.module003_participation_generate'))

            if not form.id.data:
                if course:
                    participation = Actividad(
                            course_id = course.id,
                            activity_name = form.activity_name.data,
                            activity_description =  form.activity_description.data,
                            date_expire=datetime.datetime.combine(form.date_expire.data, form.time_expire.data))
                    db.session.add(participation)
                    db.session.commit()
                    flash("Activity {} created successfully".format(participation.activity_name))
                else:
                    flash("Error selecting course")
                return redirect(url_for('module003.module003_participation_generate'))
            else:
                activity= Actividad.query.get(form.id.data)

                activity.activity_name=form.activity_name.data
                activity.activity_description=form.activity_description.data
                activity.course_id=form.course_id.data
                activity.date_expire=datetime.datetime.combine(form.date_expire.data, form.time_expire.data)

                db.session.commit()
                flash("Participation code {} updated successfully".format(activity.activity_name))
                return redirect(url_for('module003.module003_participation_generate'))
        except:
            db.session.rollback()
            flash("Error creating / updating participation!")

    elif ('rowid' in request.args):
        participation = Actividad.query.get(request.args.get('rowid'))
        form = ParticipationCodeForm(id = participation.id,
                                    course_id = participation.course_id,
                                    activity_name = participation.activity_name,
                                    activity_description =  participation.activity_description,
                                    date_expire=participation.date_expire,
                                    time_expire=participation.date_expire)
    else:
        form = ParticipationCodeForm(course_id=0)


    participations = Actividad.query.filter(Actividad.id>=0)
    participations = db.session.query(Actividad, Course).join(Course).filter(Actividad.course_id==Course.id, Course.user_id==current_user.id).all()

    all_courses = Follow.query.filter(Follow.user_id == current_user.id)
    all_courses_formated = []

    for course in all_courses:
        all_courses_formated.append({"id":course.course_id,"name":course.course_name})

    for course in Course.query.filter_by(user_id=current_user.id):
        form.course_id.choices += [(course.id,  str(course.id) + ' - ' + course.institution_name + ' - ' + course.name)]
    return render_template('module003_participation_generate.html',module="module003", form=form, rows=participations, all_courses_formated=all_courses_formated)

@module003.route('/activity/<course_id>/<activity_id>',methods=['GET','POST'])
@login_required
def module003_activity(activity_id, course_id):
    form = EntregaForm()
    if request.method == 'POST':
        files = request.files.getlist("files[]")
        activity = Actividad.query.filter(Actividad.id==activity_id).first()
        if activity:
            entrega_db= Entregas.query.filter(Entregas.activity_id==activity.id, Entregas.user_id==current_user.id).first()
            if not entrega_db:
                entrega=Entregas(
                        activity_id = activity.id,
                        user_id = current_user.id,
                        num_files = len(files),
                        content = form.content.data
                    )
                db.session.add(entrega)


            else:
                entrega_db.content=form.content.data
                entrega_db.num_files += len(files)
            db.session.commit()
            entrega_db= Entregas.query.filter(Entregas.activity_id==activity.id, Entregas.user_id==current_user.id).first()
            if files:
                n=entrega_db.num_files-len(files)
                for file in files:
                    n+=1
                    if file.filename == "":
                        flash("No filename")
                    if allowed_file(file.filename):
                        now = datetime.datetime.now()
                        # dd/mm/YY H:M:S
                        dt_string = now.strftime("%d-%m-%Y--%H:%M:%S")
                        filename = str(current_user.id)+'_'+str(activity.id)+'_'+str(n)+'_'+dt_string+'_'+secure_filename(file.filename)
                        basedir = os.path.abspath(os.path.dirname(filename))
                        file.save(os.path.join(app.config["UPLOADED_IMAGES_DEST"], filename))
                        flash("File saved")
                    else:
                        entrega_db.num_files -= 1
                        n -= 1
                        db.session.commit()
                        flash("That file extension is not allowed")
            else:
                flash("Not files")
            flash("Activity uploaded successfully")
        else:
            flash("Error: activity not found")
        return redirect(request.url)
    else:
        activity = Actividad.query.filter(Actividad.id==activity_id).first()
        act = []

        ##
        all_activities = Actividad.query.filter(Actividad.course_id == course_id)
        all_activities_formated = []
        for activity_in in all_activities:
            all_activities_formated.append({"id":activity_in.id,"name":activity_in.activity_name})
        ##

        if activity:
            act.append({
                'name': activity.activity_name,
                'descripcion': activity.activity_description,
                'expire_date':activity_in.date_expire,
                'expire_timestamp':activity_in.date_expire
                })
            course = Course.query.filter(Course.id==activity.course_id).first()
            if course.user_id is current_user.id:   #Ruta para el profesor
                all_entregas = Entregas.query.filter(Entregas.activity_id==activity.id).all()
                all_entregas_formated = []
                for entrega in all_entregas:
                    nota = Nota.query.filter(Nota.actividad_id==activity.id, Nota.user_id==entrega.user_id).first()
                    if nota:
                        nota_uni=nota.nota
                    else:
                        nota_uni=0
                    usuario = User.query.filter(User.id == entrega.user_id).first()
                    files_list=[]
                    for filename in os.listdir(app.config['UPLOADED_IMAGES_DEST']):
                        name_file=filename.split("_")
                        if name_file[0]==str(usuario.id) and name_file[1]==str(activity.id):
                            files_list.append(filename)
                    all_entregas_formated.append({"user_name":usuario.username,"user_id":usuario.id,"act_id":activity.id,"content":entrega.content,"num_files":entrega.num_files,"files_list":files_list,"nota":nota_uni,"fecha_entrega":entrega.date_created,"fecha_modificacion":entrega.date_modified,"entrega_timestamp":entrega.date_created})

                return  render_template('module003_activity_prof.html', module="module003", act=act, form=form, all_activities_formated=all_activities_formated, course_id=course_id,all_entregas_formated=all_entregas_formated)
            else:
                entrega=Entregas.query.filter(Entregas.activity_id==activity.id).first()
                files_list=[]
                if entrega:
                    nota=Nota.query.filter(Nota.user_id==current_user.id,Nota.actividad_id==activity.id).first()
                    if nota:
                        form = EntregaForm(content = entrega.content, nota=nota.nota)
                    else:
                        form = EntregaForm(content = entrega.content)

                    for filename in os.listdir(app.config['UPLOADED_IMAGES_DEST']):
                        name_file=filename.split("_")
                        if name_file[0]==str(current_user.id) and name_file[1]==str(activity.id):
                            files_list.append(filename)

                return  render_template('module003_activity_alum.html', module="module003", act=act, form=form, all_activities_formated=all_activities_formated, course_id=course_id, activity_id=activity.id, files_list=files_list)
        else:
            flash("No hay actividades")
        return redirect(url_for('module003.module003_participation_generate'))


@module003.route('/nota', methods=['GET', 'POST'])
@login_required
def nota():
    if request.method == 'POST':
        nota=request.get_data().decode("utf-8")

        nota=nota.split("_")
        actividad= Actividad.query.filter(Actividad.id==nota[1]).first()
        curso=Course.query.filter(Course.id==actividad.course_id).first()
        if curso.user_id==current_user.id:
            nota_check=Nota.query.filter(Nota.user_id==nota[2], Nota.actividad_id==nota[1]).first()
            if not nota_check:
                nota_db=Nota(nota=nota[0], actividad_id=nota[1], user_id=nota[2])
                db.session.add(nota_db)
            else:
                nota_check.nota=nota[0]
            db.session.commit()
            return "OK_query"
    return "OK"

@module003.route('/uploads/<path:filename>', methods=['GET', 'POST'])
@login_required
def download(filename):
    name=filename.split("_")
    if name[0]==str(current_user.id) or current_user.profile == "admin" :
        try:
            return send_file(os.path.join(app.config["UPLOADED_IMAGES_DEST"], filename))
        except:
            flash("This file doesn't exist")
    else:
        flash("You don't have access to this file")
    return redirect(url_for('module003.module003_participation_generate'))


@module003.route('/course/<course_id>',methods=['GET','POST'])
@login_required
def module003_course(course_id):
    if request.method == 'POST':
        return 'OK'
    else:
        all_activities = Actividad.query.filter(Actividad.course_id == course_id)
        all_activities_formated = []
        for activity in all_activities:
            all_activities_formated.append({"id":activity.id,"name":activity.activity_name})

    return render_template('module003_course.html', module="module003", all_activities_formated=all_activities_formated, course_id=course_id)




@module003.route('/test')
def module003_test():
    return 'OK'





















