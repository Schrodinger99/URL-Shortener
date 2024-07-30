from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_admin import Admin 
from flask_admin.contrib.sqla import ModelView
from .models import User, Link, Click

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
admin = Admin(template_mode = 'bootstrap3')

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    admin.init_app(app)
    
    from .admin import MyAdminIndexView, MyModelView
    
    #Vistas de administración
    admin.add_view(MyModelView(User, db.session))
    admin.add_view(MyModelView(Link, db.session))
    admin.add_view(MyModelView(Click, db.session))
    
    with app.app_context():
        from . import routes, models, errors
        db.create_all()
        
    return app