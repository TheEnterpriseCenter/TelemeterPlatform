from flask_login import *
from db_models import *

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.login_message = u"You must be logged in to view this page."
login_manager.login_message_category = "info"


class UserLogin(UserMixin):
    def __init__(self, first, last, phone, email, org, role, uploadid, password, user_id):
        self.first = first
        self.last = last
        self.phone = phone
        self.email = email
        self.org = org
        self.role = role
        self.uploadid = uploadid
        self.id = user_id
        self.password = password
        self.user_id = user_id

    @classmethod
    def getByEmail(cls, email):
        query = User.query.filter(User.email == email).first()
        if query is not None:
            query_dict = (DBResultSet.as_dict(query))['records'][0]
            return cls(query_dict['first'], query_dict['last'], query_dict['phone'], query_dict['email'], query_dict['org'],
                       query_dict['role'], query_dict['uploadid'], query_dict['password'], query_dict['id'])
        else:
            return None

    @classmethod
    def getById(cls, user_id):
        query = User.query.filter(User.id == user_id).first()
        if query is not None:
            query_dict = (DBResultSet.as_dict(query))['records'][0]
            return cls(query_dict['first'], query_dict['last'], query_dict['phone'], query_dict['email'],
                       query_dict['org'],
                       query_dict['role'], query_dict['uploadid'], query_dict['password'], query_dict['id'])
        else:
            return None


@login_manager.user_loader
def load_user(user_id):
    return UserLogin.getById(user_id)


@login_manager.unauthorized_handler
def unauthorized():
    if current_user and  hasattr(current_user, 'role'):
        if current_user.role == 'admin' or current_user.role == 'teacher' or current_user.role == 'technician':
            return "Unauthorized access"
    else:
        return flask.redirect(flask.url_for('login'))