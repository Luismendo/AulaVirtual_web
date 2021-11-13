from application import get_app
from flask_login import login_required, login_user, logout_user, current_user
from flask import render_template, request, redirect, url_for, flash
from sqlalchemy import or_
from models import User, get_db
from werkzeug.security import generate_password_hash, check_password_hash
from mail import send_email
from forms import RegisterForm, ProfileForm, LoginForm, RecoverPasswdForm
import py_avataaars as pa
from werkzeug.utils import secure_filename
import os
from flask_uploads import configure_uploads, IMAGES, UploadSet

app = get_app()
db = get_db()



@app.route('/profile',methods=['GET','POST'])
@login_required
def profile():
    form = ProfileForm(email=current_user.email,
                       username=current_user.username,
                       profile=current_user.profile)
    return render_template("profile.html",module="profile", form=form)


@app.route('/login',methods=['GET','POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.filter(or_(User.email==form.emailORusername.data,
                                         User.username==form.emailORusername.data)).first()
            if not user or not check_password_hash(user.password, form.password.data):
                flash("Wrong user or Password!")
            elif user.confirmed:
                login_user(user, remember=form.remember.data)
                flash("Welcome back {}".format(current_user.username))
                return redirect(url_for('dashboard'))
            else:
                flash("User not confirmed. Please visit your email to confirm your user.")


    return render_template('login.html',module="login", form=form)

import random
@app.route('/signup',methods=['GET','POST'])
def signup():
    form = RegisterForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            # Ejercicio - juntar la dos partes!!! Coger del formulario y meter en base de datos!
            try:
                password_hashed=generate_password_hash(form.password.data,method="sha256")
                flash('hasta aqui por lo menos')
                url_imagen = avatarGenerator() #URL DESDE module002
                newuser = User(email=form.email.data,
                               username=form.username.data,
                               userhash=str(random.getrandbits(128)),
                               password=password_hashed,
                               img_name=url_imagen)
                db.session.add(newuser)
                db.session.commit()
                send_email(newuser.email,'Please, confirm email / Por favor, confirmar correo.','mail/new_user',user=newuser,url=request.host, newpassword=password_hashed)
                flash("Great, your user was created successfully please visit your email {} to confirm your email / Muy bien, ahora visite su correo electrónico {} para confirmar el correo.".format(newuser.email,newuser.email))
                return redirect(url_for('login'))
            except:
                db.session.rollback()
                flash("Error creating user!")
    return render_template('signup.html',module="signup", form=form)


#######################CREAMOS LA IMAGEN DEL USUARIO
import time
def avatarGenerator():

    current = time.strftime("%Y%m%d%H%M%S")
    filename = 'module002/static/{}.png'.format(current)

    def r(enum_):
        return random.choice(list(enum_))

    avatar = pa.PyAvataaar(
        style=pa.AvatarStyle.CIRCLE,
        skin_color= r(list(pa.SkinColor)),
        hair_color= r(list(pa.HairColor)),
        facial_hair_type=r(list(pa.FacialHairType)),
        facial_hair_color=r(pa.HairColor),
        top_type=r(pa.TopType),
        hat_color=r(pa.Color),
        mouth_type=r(pa.MouthType),
        eye_type=r(pa.EyesType),
        eyebrow_type=r(pa.EyebrowType),
        nose_type=r(pa.NoseType),
        accessories_type=r(pa.AccessoriesType),
        clothe_type=r(pa.ClotheType),
        clothe_color=r(pa.Color),
        clothe_graphic_type=r(pa.ClotheGraphicType),
    )
    #avatar = pa.PyAvataaar()
    avatar.render_png_file(filename)
    return current
##############################


@app.route('/confirmuser/<username>/<userhash>/',methods=['GET'])
def confirmuser(username,userhash):
    user = User.query.filter_by(username=username).first()
    if not user:
        flash('Invalid url.')
    elif userhash != user.userhash:
        flash('Invalid url.')
    elif user.confirmed:
        flash('Url already used.')
    else:
        try:
            user.confirmed = 1
            db.session.commit()
            flash('User confirmed successfully.')
        except:
            db.session.rollback()
            flash("Error confirming user!")
    return redirect(url_for('login'))






@app.route('/changepassword',methods=['GET','POST'])
def changepassword():
    form = RecoverPasswdForm()
    if request.method == 'POST':

        if form.validate_on_submit():
            user = User.query.filter(or_(User.email==form.email.data)).first()

            if not user:
                flash("Wrong email!")
            elif user.confirmed:
                password_hashed=generate_password_hash(form.password.data,method="sha256")
                send_email(user.email,'Please, confirm passwd change / Por favor, confirmar el cambio de contraseña.','mail/new_password',user=user,url=request.host, newpassword=password_hashed)
                flash("Email has been send")
                return redirect(url_for("login"))
            else:
                flash("User not confirmed. Please visit your email to confirm your user.")
    return render_template('changepasswd.html',module="login", form=form)


@app.route('/confirmpassword/<username>/<userhash>/<newpassword>/',methods=['GET'])
def confirmpassword(username,userhash,newpassword):
    user = User.query.filter_by(username=username).first()
    if not user:
        flash('Invalid url.')
    elif userhash != user.userhash:
        flash('Invalid url.')
    elif user.password == newpassword:
        flash('Url already used.')
    else:
        try:
            user.password = newpassword
            db.session.commit()
            flash('Password successfully changed.')
        except:
            db.session.rollback()
            flash("Error changing password!")
    return redirect(url_for('login'))




@app.route('/logout')
@login_required
def logout():
    flash("See you soon {}".format(current_user.username))
    logout_user()
    return redirect(url_for('index'))


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html',module="home")


@app.route('/')
def index():
    return render_template('index.html',module="home")


########

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

@app.route("/tarea", methods=["GET", "POST"])
@login_required
def tarea():
    if request.method == "POST":
        files = request.files.getlist("files[]")
        if files:
            for file in files:
                if file.filename == "":
                    flash("No filename")
                if allowed_file(file.filename):
                    filename = str(current_user)+'_'+secure_filename(file.filename)
                    basedir = os.path.abspath(os.path.dirname(filename))
                    file.save(os.path.join(app.config["UPLOADED_IMAGES_DEST"], filename))
                    flash("File saved")
                else:
                    flash("That file extension is not allowed")
            return redirect(request.url)
    return render_template("task.html")

########

@app.errorhandler(500)
def internal_server_error(e):
    db.session.rollback()
    return render_template("500.html"), 500

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

@app.errorhandler(403)
def access_denied(e):
    return render_template("403.html"), 403
