from flask import Flask, request, session, render_template
from flask_login import *
from db_models import *
from login_manager import *

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:0000@localhost:5432/NameHere'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'SNEAKY SNEAKY'

db.init_app(app)

login_manager.init_app(app)


# def get_db_connection():
#     if db:
#         return db.
#     return db


def search_stuff(tag):
    query = User.query.filter(User.first == tag).first()
    return DBResultSet.as_dict(query)


@app.route('/', methods=['GET', 'POST'])
def index():

    # me = User('Caleb', 'Campbell', '4232345234', 'assgas@hello.com', 'UTC', 'admin', 3)
    # db.session.add(me)
    # db.session.commit()
    # dict1 = {'tags': ['tag1', 'tag2', 'tag3']}
    # dict2 = {'students': ['student1', 'student2']}
    # exp = ExpData(flask.json.dumps(dict1), 'Trey', flask.json.dumps(dict2))
    # db.session.add(exp)
    # db.session.commit()
    # exp_query = ExpData.query.all()
    # user = User.query.all()
    # print(db.metadata.tables)
    # return DBResultSet.as_json(exp_query)
    if request.method == 'GET':
        return render_template("index.j2")
    else:
        data = request.form['search_form']
        foo = search_stuff(data)
        print(foo)
        return render_template("search_results.j2", result = foo)


@app.route('/tables/<table>', methods=['GET'])
def tables(table=None):
    for table_class in db.Model.__subclasses__():
        # print(table_class.__tablename__)
        if table_class.__tablename__ == table:
            return DBResultSet.as_json(table_class.query.all())
    return 'Specified Table Not Found in Database'


@app.route('/tables/display/<table>', methods=['GET'])
def display_table(table=None):
    for table_class in db.Model.__subclasses__():
        if table_class.__tablename__ == table:
            records = DBResultSet.as_dict(table_class.query.all())
            print(records)
            return render_template("nav_bar_default.j2", result=records, name=table)
    return 'Specified Table Not Found in Database'


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if password == UserLogin.get(username).password:
            user = UserLogin.get(username)
            login_user(user)
            return flask.redirect(flask.url_for('index'))
        else:
            return ""

    return render_template("login.j2")


























#### michaelwashere ####
#####no functionality for the below sections, however links are properly established#####


@app.route('/teacher_start_session', methods=['GET'])
def teacher_start_session():
    #start session button functionality goes here
    return render_template("teacher_start_session.j2")


@app.route('/contact_us', methods=['GET'])
def contact_us():
    return render_template("contact_us.j2")


@app.route('/admin_login', methods=['GET'])
def admin_login():
    return render_template("admin_login.j2")

@app.route('/tech_login', methods=['GET'])
def tech_login():
    return render_template("tech_login.j2")


@app.route('/tech_start_session', methods=['GET'])
def tech_start_session():
    return render_template("tech_start_session.j2")

@app.route('/teacher_session', methods=['GET'])
def teacher_session():
    return render_template("teacher_session.j2")


@app.route('/profile', methods=['GET'])
def profile():
    return render_template("profile.j2")

@app.route('/search', methods=['GET'])
def search_page():
    return render_template("search_page.j2")

@app.route('/search_results', methods=['GET'])
def search_results():
    return render_template("search_results.j2")

@app.route('/admin_create_new_user', methods=['GET'])
def admin_create_new_user():
    return render_template("admin_create_new_user.j2")

@app.route('/admin_delete_user', methods=['GET'])
def admin_delete_user():
    return render_template("admin_delete_user.j2")

@app.route('/admin_modify_user', methods=['GET'])
def admin_modify_user():
    return render_template("admin_modify_user.j2")

@app.route('/admin_delete_asset', methods=['GET'])
def admin_delete_asset():
    return render_template("admin_delete_asset.j2")

@app.route('/admin_create_new_asset', methods=['GET'])
def admin_create_new_asset():
    return render_template("admin_create_new_asset.j2")

@app.route('/admin_delete_experiment', methods=['GET'])
def admin_delete_experiment():
    return render_template("admin_delete_experiment.j2")

@app.route('/admin_delete_tag', methods=['GET'])
def admin_delete_tag():
    return render_template("admin_delete_tag.j2")

@app.route('/admin_delete_upload_acct', methods=['GET'])
def admin_delete_upload_acct():
    return render_template("admin_delete_upload_acct.j2")

@app.route('/admin_modify_upload_acct', methods=['GET'])
def admin_modify_upload_acct():
    return render_template("admin_modify_upload_acct.j2")

@app.route('/admin_create_new_upload_acct', methods=['GET'])
def admin_create_new_upload_acct():
    return render_template("admin_create_new_upload_acct.j2")

@app.route('/tech_create_new_teacher', methods=['GET'])
def tech_create_new_teacher():
    return render_template("tech_create_new_teacher.j2")

@app.route('/tech_modify_teacher', methods=['GET'])
def tech_modify_teacher():
    return render_template("tech_modify_teacher.j2")

@app.route('/tech_change_teacher_password', methods=['GET'])
def tech_change_teacher_password():
    return render_template("tech_change_teacher_password.j2")







if __name__ == "__main__":
    # db.create_all()
    app.run(port=5001, debug=True)


# @login_manager.user_loader
# def load_user(user_id):
#     return User.get(user_id)