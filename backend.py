from flask import Flask, request, session, render_template, abort, jsonify
import json
from flask_login import *
from db_models import *
from login_manager import *

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Treysla5@localhost:9998/NameHere'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'SNEAKY SNEAKY'

db.init_app(app)

login_manager.init_app(app)


@app.route('/', methods=['GET', 'POST'])
def index():
    # me = User('Caleb', 'Campbell', '4232345234', 'assgas@hello.com', 'UTC', 'admin', 3)
    # db.session.add(me)
    # db.session.commit()
    # dict1 = {'tags': ['shit', 'cell', 'animal', 'skin', 'keratin']}
    # dict2 = {'students': ['brittneyk@org.edu', 'carl@org.edu']}
    # exp = ExpData(flask.json.dumps(dict1), 'Trey', flask.json.dumps(dict2), "Experiment #4")
    # add_experiment(exp, dict1)
    # db.session.add(exp)
    # db.session.commit()
    # exp_query = ExpData.query.all()
    # user = User.query.all()
    # print(db.metadata.tables)
    # return DBResultSet.as_json(exp_query)
    if request.method == 'GET':
        return render_template("index.j2")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = UserLogin.getByEmail(username)
        if user is not None and password == user.password:
            login_user(user)
            session['logged_in'] = True
            return flask.redirect(flask.url_for('index'))
        else:
            return render_template("login.j2", login_message='Login Failed: Invalid Credentials')

    return render_template("login.j2", login_message='')


@app.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    session['logged_in'] = False
    return flask.redirect(flask.url_for('index'))


@app.route('/contact_us', methods=['GET'])
def contact_us():
    return render_template("contact_us.j2")


@app.route('/teacher_start_session', methods=['GET'])
@login_required
def teacher_start_session():
    #start session button functionality goes here
    return render_template("teacher_start_session.j2")


@app.route('/admin_login', methods=['GET'])
@login_required
def admin_login():
    return render_template("admin_login.j2")


@app.route('/tech_login', methods=['GET'])
@login_required
def tech_login():
    return render_template("tech_login.j2")


@app.route('/tech_start_session', methods=['GET'])
@login_required
def tech_start_session():
    return render_template("tech_start_session.j2")


@app.route('/teacher_session', methods=['GET'])
@login_required
def teacher_session():
    return render_template("teacher_session.j2")


@app.route('/search_experiments', methods=['GET', 'POST'])
def search_experiments():
    results = search_stuff(request.form['tags'])
    return render_template("search_results.j2", results=results)


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        if request.form['profile_action'] == 'profile':
            if request.form['password_submit'] == current_user.password:
                user = User.query.filter(User.id == current_user.user_id).first()
                user.first = request.form['first']
                user.last = request.form['last']
                user.phone = request.form['phone']
                user.email = request.form['email']
                user.org = request.form['org']
                db.session.commit()
                current_user.first = request.form['first']
                current_user.last = request.form['last']
                current_user.phone = request.form['phone']
                current_user.email = request.form['email']
                current_user.org = request.form['org']
        elif request.form['profile_action'] == 'password':
            if request.form['old_pass'] == current_user.password and request.form['new_pass'] == request.form['new_pass_confirm']:
                user = User.query.filter(User.id == current_user.user_id).first()
                user.password = request.form['new_pass']
                db.session.commit()
                current_user.password = request.form['new_pass']
    return render_template("profile.j2")


# TODO: if admin and logged in
@app.route('/admin_create_new_user', methods=['GET', 'POST'])
@login_required
def admin_create_new_user():
    if current_user.role != 'admin':
        return app.login_manager.unauthorized()

    if request.method == 'POST':
        if request.form['first'] and request.form['last'] and request.form['phone']\
                and request.form['email'] and request.form['org'] and request.form['role']:
            # TODO: upload id needs to be changed
            user = User(request.form['first'], request.form['last'], request.form['phone'], request.form['email'],
                        request.form['org'], request.form['role'], 1, 'password')
            db.session.add(user)
            db.session.commit()
    return render_template("admin_create_new_user.j2")


@app.route('/admin_delete_user', methods=['GET', 'POST'])
@login_required
def admin_delete_user():
    if current_user.role != 'admin':
        return app.login_manager.unauthorized()

    if request.method == 'POST':
        user_id = request.form.get('user_select', None)
        if request.form['user_action'] == 'delete' and user_id is not None:
            user = User.query.filter(User.id == user_id).first()
            db.session.delete(user)
            db.session.commit()
        elif request.form['user_action'] == 'modify' and user_id is not None:
            user = User.query.filter(User.id == user_id).first()
            return flask.redirect(flask.url_for('admin_modify_user', user_id=user.id))
    query = User.query.all()
    users = DBResultSet.as_dict(query)
    return render_template("admin_delete_user.j2", users=users)


@app.route('/admin_modify_user/<user_id>', methods=['GET', 'POST'])
@login_required
def admin_modify_user(user_id=None):
    if current_user.role != 'admin':
        return app.login_manager.unauthorized()

    user = User.query.filter(User.id == user_id).first()
    if request.method == 'POST':
        if request.form['profile_action'] == 'profile':
            user.first = request.form['first']
            user.last = request.form['last']
            user.phone = request.form['phone']
            user.email = request.form['email']
            user.org = request.form['org']
            user.role = request.form['role']
            user.uploadid = request.form['uploadid']
            db.session.commit()
        elif request.form['profile_action'] == 'password':
            if request.form['new_pass'] == request.form['new_pass_confirm']:
                user.password = request.form['new_pass']
                db.session.commit()
    return render_template("admin_modify_user.j2", user=user)


@app.route('/admin_delete_asset', methods=['GET', 'POST'])
@login_required
def admin_delete_asset():
    if current_user.role != 'admin':
        return app.login_manager.unauthorized()

    if request.method == 'POST':
        asset_id = request.form.get('asset_select', None)
        if request.form['asset_action'] == 'delete' and asset_id is not None:
            asset = Asset.query.filter(Asset.id == asset_id).first()
            db.session.delete(asset)
            db.session.commit()
        elif request.form['asset_action'] == 'modify' and asset_id is not None:
            asset = Asset.query.filter(Asset.id == asset_id).first()
            return flask.redirect(flask.url_for('admin_modify_asset', asset_id=asset.id))
    query = Asset.query.all()
    assets = DBResultSet.as_dict(query)
    return render_template("admin_delete_asset.j2", assets=assets)


@app.route('/admin_modify_asset/<asset_id>', methods=['GET', 'POST'])
@login_required
def admin_modify_asset(asset_id=None):
    if current_user.role != 'admin':
        return app.login_manager.unauthorized()

    asset = Asset.query.filter(Asset.id == asset_id).first()
    if request.method == 'POST':
        asset.name = request.form['name']
        asset.location = request.form['location']
        asset.ip_address = request.form['ip']
        db.session.commit()
    return render_template("admin_modify_asset.j2", asset=asset)


@app.route('/admin_create_new_asset', methods=['GET', 'POST'])
@login_required
def admin_create_new_asset():
    if current_user.role != 'admin':
        return app.login_manager.unauthorized()

    if request.method == 'POST':
        name = request.form.get('name', None)
        location = request.form.get('location', None)
        ip_address = request.form.get('ip', None)
        if name is not None and location is not None and ip_address is not None:
            asset = Asset(name, location, ip_address)
            db.session.add(asset)
            db.session.commit()
    return render_template("admin_create_new_asset.j2")


@app.route('/admin_delete_experiment', methods=['GET', 'POST'])
@login_required
def admin_delete_experiment():
    if current_user.role != 'admin':
        return app.login_manager.unauthorized()

    if request.method == 'GET':
        query = ExpData.query.all()
        action = 'all_exps'
        exp_ids = []
    elif request.method == 'POST':
        if request.form['action'] == 'all_exps':
            query = ExpData.query.all()
            for experiment in query:
                if request.form.get('experiment_select:' + str(experiment.id)) is not None:
                    experiment_id = request.form.get(('experiment_select:' + str(experiment.id)), None)
                    if experiment_id is not None:
                        experiment = ExpData.query.filter(ExpData.id == experiment_id).first()
                        remove_experiment(experiment, experiment.as_dict()['tags'])
            query = ExpData.query.all()
            action = 'all_exps'
            exp_ids = []
        elif request.form['action'] == 'select_exps':
            exp_ids = json.loads(request.form['exp_ids'])
            query = ExpData.query.filter(ExpData.id.in_(exp_ids)).all()
            for experiment in query:
                if request.form.get('experiment_select:' + str(experiment.id)) is not None:
                    experiment_id = request.form.get(('experiment_select:' + str(experiment.id)), None)
                    if experiment_id is not None:
                        experiment = ExpData.query.filter(ExpData.id == experiment_id).first()
                        remove_experiment(experiment, experiment.as_dict()['tags'])
                        print(exp_ids)
                        print(experiment_id)
            query = ExpData.query.filter(ExpData.id.in_(exp_ids)).all()
            action = 'select_exps'
    records_list = []
    for record in query:
        records_list.append(record.as_dict())
    records_dict = {'records': records_list}
    return render_template("admin_delete_experiment.j2", experiments=records_dict, action=action, exp_ids=exp_ids)


@app.route('/admin_delete_tag', methods=['GET', 'POST'])
@login_required
def admin_delete_tag():
    if current_user.role != 'admin':
        return app.login_manager.unauthorized()

    query = Tags.query.all()
    if request.method == 'POST':
        for item in query:
            if request.form.get('tag_select:' + str(item.name)) is not None:
                tag_id = request.form.get(('tag_select:' + str(item.name)), None)
                if tag_id is not None:
                    tag = Tags.query.filter(Tags.name == tag_id).first()
                    remove_tag(tag)
        query = Tags.query.all()
    return render_template("admin_delete_tag.j2", tags=DBResultSet.as_dict(query))


@app.route('/admin_delete_upload_acct', methods=['GET', 'POST'])
@login_required
def admin_delete_upload_acct():
    if current_user.role != 'admin':
        return app.login_manager.unauthorized()

    if request.method == 'POST':
        account_id = request.form.get('account_select', None)
        if request.form['account_action'] == 'delete' and account_id is not None:
            account = UploadAcct.query.filter(UploadAcct.id == account_id).first()
            db.session.delete(account)
            db.session.commit()
        elif request.form['account_action'] == 'modify' and account_id is not None:
            account = UploadAcct.query.filter(UploadAcct.id == account_id).first()
            return flask.redirect(flask.url_for('admin_modify_upload_acct', account_id=account.id))
    query = UploadAcct.query.all()
    accounts = DBResultSet.as_dict(query)
    return render_template("admin_delete_upload_acct.j2", accounts=accounts)


@app.route('/admin_modify_upload_acct/<account_id>', methods=['GET', 'POST'])
@login_required
def admin_modify_upload_acct(account_id=None):
    if current_user.role != 'admin':
        return app.login_manager.unauthorized()

    account = UploadAcct.query.filter(UploadAcct.id == account_id).first()
    if request.method == 'POST':
        account.username = request.form['username']
        account.password = request.form['password']
        db.session.commit()
    return render_template("admin_modify_upload_acct.j2", account=account)


@app.route('/admin_create_new_upload_acct', methods=['GET', 'POST'])
@login_required
def admin_create_new_upload_acct():
    if current_user.role != 'admin':
        return app.login_manager.unauthorized()

    if request.method == 'POST':
        username = request.form.get('username', None)
        password = request.form.get('password', None)
        if username is not None and password is not None:
            account = UploadAcct(username, password)
            db.session.add(account)
            db.session.commit()
    return render_template("admin_create_new_upload_acct.j2")


@app.route('/tech_create_new_teacher', methods=['GET', 'POST'])
@login_required
def tech_create_new_teacher():
    if current_user.role != 'technician':
        return app.login_manager.unauthorized()

    if request.method == 'POST':
        if request.form['first'] and request.form['last'] and request.form['phone']\
                and request.form['email'] and request.form['org']:
            # TODO: upload id needs to be changed
            user = User(request.form['first'], request.form['last'], request.form['phone'], request.form['email'],
                        request.form['org'], 'teacher', 1, 'password')
            db.session.add(user)
            db.session.commit()
    return render_template("tech_create_new_teacher.j2")


@app.route('/tech_delete_teacher', methods=['GET', 'POST'])
@login_required
def tech_delete_teacher():
    if current_user.role != 'technician':
        return app.login_manager.unauthorized()

    if request.method == 'POST':
        user_id = request.form.get('user_select', None)
        if request.form['user_action'] == 'delete' and user_id is not None:
            user = User.query.filter(User.id == user_id).first()
            db.session.delete(user)
            db.session.commit()
        elif request.form['user_action'] == 'modify' and user_id is not None:
            user = User.query.filter(User.id == user_id).first()
            return flask.redirect(flask.url_for('tech_modify_teacher', user_id=user.id))
    query = User.query.filter(User.role == 'teacher').all()
    users = DBResultSet.as_dict(query)
    return render_template("tech_delete_teacher.j2", users=users)


@app.route('/tech_modify_teacher/<user_id>', methods=['GET', 'POST'])
@login_required
def tech_modify_teacher(user_id=None):
    if current_user.role != 'technician':
        return app.login_manager.unauthorized()

    user = User.query.filter(User.id == user_id).first()
    if request.method == 'POST':
        if request.form['profile_action'] == 'profile':
            user.first = request.form['first']
            user.last = request.form['last']
            user.phone = request.form['phone']
            user.email = request.form['email']
            user.org = request.form['org']
            db.session.commit()
        elif request.form['profile_action'] == 'password':
            if request.form['new_pass'] == request.form['new_pass_confirm']:
                user.password = request.form['new_pass']
                db.session.commit()
    return render_template("tech_modify_teacher.j2", user=user)


def search_stuff(tags):
    tag_split = tags.split(',')
    experiments = []
    exp_hits = {}
    for tag in tag_split:
        tag_query = Tags.query.filter(Tags.name == tag.strip().lower()).first()
        if tag_query is not None:
            for exp_id in tag_query.exp_ids:
                if str(exp_id) not in exp_hits:
                    exp_hits[str(exp_id)] = 1
                else:
                    exp_hits[str(exp_id)] += 1
        else:
            exp_query = ExpData.query.filter(func.lower(ExpData.name) == tag.strip().lower()).all()
            if exp_query is not None and len(exp_query) > 0:
                for exp in exp_query:
                    if str(exp.id) not in exp_hits:
                        exp_hits[str(exp.id)] = 1
                    else:
                        exp_hits[str(exp.id)] += 1
            else:
                exp_query = ExpData.query.filter(func.lower(ExpData.teacher) == tag.strip().lower()).all()
                if exp_query is not None and len(exp_query) > 0:
                    for exp in exp_query:
                        if str(exp.id) not in exp_hits:
                            exp_hits[str(exp.id)] = 1
                        else:
                            exp_hits[str(exp.id)] += 1
    if len(exp_hits) > 0:
        exp_hits = sorted(exp_hits.items(), key=lambda item: item[1], reverse=True)
        print(exp_hits)
        for key, value in exp_hits:
            exp_query = ExpData.query.filter(ExpData.id == int(key)).first()
            if exp_query is not None:
                experiments.append(exp_query.as_dict())
    return {'records': experiments}


if __name__ == "__main__":
    app.run(port=5001, debug=True)