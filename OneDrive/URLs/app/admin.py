from flask_admin import AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user, login_required
from . import db, app
from .models import User, Link, Click

class MyAdminIndexView(AdminIndexView):
    @expose('/')
    @login_required
    def index(self):
        if not current_user.is_admin:
            return redirect(url_for('index'))
        return super(MyAdminIndexView,self).index()

class MyModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

admin.add_view(MyModelView(User, db.session))
admin.add_view(MyModelView(Link, db.session))
admin.add_view(MyModelView(Click, db.session))