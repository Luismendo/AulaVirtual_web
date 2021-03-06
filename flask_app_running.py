import json
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand



with open('configuration.json') as json_file:
    configuration = json.load(json_file)

from application import init_app
app = init_app(__name__)

#from paquete.codigo import objeto
#from carperta.codigopython import objeto
from module001.views_01 import module001
from module002.views_02 import module002
from module003.views_03 import module003

app.register_blueprint(module001, url_prefix="/course")
app.register_blueprint(module002, url_prefix="/blog")
app.register_blueprint(module003, url_prefix="/assignment")

# CONFIG- START
app.config['SECRET_KEY'] = configuration['SECRET_KEY']

if configuration['MODE'] == 'production':
    SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}?auth_plugin=mysql_native_password".format(
        username=configuration['mysql_username'],
        password=configuration['mysql_password'],
        hostname=configuration['mysql_hostname'],
        databasename=configuration['mysql_databasename']
        )
    app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_POOL_RECYCLE'] = 299

else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./database/user.db'


app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = configuration['gmail_username']
app.config['MAIL_PASSWORD'] = configuration['gmail_password']

app.config['FLASKY_MAIL_SUBJECT_PREFIX'] = '[Aula Virtual] '
app.config['FLASKY_MAIL_SENDER'] = 'Prof. Manoel Gadi'


#Mail init start
from mail import init_mail
mail = init_mail(app)
#END

from flask_bootstrap import Bootstrap
Bootstrap(app)

# ADMIN - START
from admin import init_admin
admin = init_admin(app)
# ADMIN - END


# MODEL - START # ORM - Object Relational Mapping -Magico que se conecta a casi cualquiera base de datos.
from models import init_db, User
db =  init_db(app)# class db extends app
# MODEL - END


# MIGRATE - START
migrate = Migrate(app,db)
manager = Manager(app)
manager.add_command('db',MigrateCommand)
# MIGRATE - END



# LOGIN - START
from flask_login import LoginManager
login_manager = LoginManager() # Creando el objeto de la clase Login
login_manager.init_app(app) # Asociando el login a la app
login_manager.login_view = 'login' # Donde voy si no estoy loggeado

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id) # flask_login no tiene porque saber de la base de datos.
# LOGIN - END


import views


if __name__ == '__main__':
    manager.run()

