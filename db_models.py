from sqlalchemy import func
from sqlalchemy.ext.mutable import Mutable
from sqlalchemy.dialects import postgresql
from flask_sqlalchemy import SQLAlchemy
from flask import Response
import json
import flask
from datetime import date

db = SQLAlchemy()


def add_experiment(exp, tags):
    db.session.add(exp)
    db.session.commit()
    for name in tags['tags']:
        tag = Tags.query.filter(Tags.name == name.lower()).first()
        if tag is None:
            exp_ids = [exp.id]
            tag = Tags(name.lower(), exp_ids)
            db.session.add(tag)
            db.session.commit()
        else:
            tag.exp_ids.append(exp.id)
            db.session.commit()


def remove_experiment(exp, tags):
    if 'tags' in tags:
        for name in tags['tags']:
            tag = Tags.query.filter(Tags.name == name.lower()).first()
            if tag is not None:
                if exp.id in tag.exp_ids:
                    tag.exp_ids.remove(exp.id)
                    db.session.commit()
    db.session.delete(exp)
    db.session.commit()


def remove_tag(tag):
    for exp_id in tag.exp_ids:
        exp = ExpData.query.filter(ExpData.id == exp_id).first()
        if exp is not None:
            exp_tags = exp.as_dict()['tags']
            if tag.name in exp_tags['tags']:
                exp_tags['tags'].remove(tag.name)
                exp_tags = flask.json.dumps(exp_tags)
                exp.tags = exp_tags
                db.session.commit()
    db.session.delete(tag)
    db.session.commit()


class DBResultSet:
    @staticmethod
    def as_dict(records):
        print(records)
        if isinstance(records, list):
            records_list = []
            for record in records:
                record_dict = {}
                for column in record.__table__.columns:
                    record_dict[column.name] = getattr(record, column.name)
                records_list.append(record_dict)
            records_dict = {'records': records_list}
        else:
            records_list = []
            record_dict = {}
            for column in records.__table__.columns:
                record_dict[column.name] = getattr(records, column.name)
            records_list.append(record_dict)
            records_dict = {'records': records_list}
        print(records_dict)
        return records_dict

    @staticmethod
    def as_json(records):
        return Response(flask.json.dumps(DBResultSet.as_dict(records)), mimetype='application/json')


class User(db.Model):
    first = db.Column(db.String(30))
    last = db.Column(db.String(30))
    phone = db.Column(db.String(11))
    email = db.Column(db.String(50), primary_key=True, nullable=False)
    org = db.Column(db.String(50))
    role = db.Column(db.String(10))
    uploadid = db.Column(db.Integer)
    password = db.Column(db.String(50))
    id = db.Column(db.Integer, nullable=False, server_default=func.nextval())

    def __init__(self, first, last, phone, email, org, role, uploadid, password):
        self.first = first
        self.last = last
        self.phone = phone
        self.email = email
        self.org = org
        self.role = role
        self.uploadid = uploadid
        self.password = password

    def __repr__(self):
        return '<User %r %r>' % (self.first, self.last)


class ExpData(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    tags = db.Column(postgresql.JSON)
    exp_date = db.Column(postgresql.TIMESTAMP(timezone=True), server_default=func.current_timestamp())
    teacher = db.Column(db.String(50))
    students = db.Column(postgresql.JSON)
    name = db.Column(db.String(80), nullable=False)
    link = db.Column(db.String(80))

    def __init__(self, tags, teacher, students, name, link):
        self.tags = tags
        self.teacher = teacher
        self.students = students
        self.name = name
        self.link = link

    def as_dict(self):
        exp_dict = \
            {
                'id': self.id,
                'name': self.name,
                'teacher': self.teacher,
                'exp_date': self.exp_date.strftime("%B %d, %Y  %I:%M %p"),
                'link': self.link
            }
        if isinstance(self.students, dict):
            exp_dict['students'] = self.students
        else:
            exp_dict['students'] = json.loads(self.students)

        if isinstance(self.tags, dict):
            exp_dict['tags'] = self.tags
        else:
            exp_dict['tags'] = json.loads(self.tags)
        return exp_dict

    def __repr__(self):
        return '<ExpData %r>' % self.tags


class Asset(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False, server_default=func.nextval())
    name = db.Column(db.String(60), nullable=False)
    location = db.Column(db.String(50), nullable=False)
    ip_address = db.Column(db.String(50), nullable=False)

    def __init__(self, name, location, ip_address):
        self.name = name
        self.location = location
        self.ip_address = ip_address

    def __repr__(self):
        return '<Asset %r>' % self.name


class UploadAcct(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False, server_default=func.nextval())
    username = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(20), nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return '<UploadAcct %r>' % self.username


class MutableList(Mutable, list):
    def append(self, value):
        list.append(self, value)
        self.changed()

    def remove(self, value):
        list.remove(self, value)
        self.changed()

    @classmethod
    def coerce(cls, key, value):
        if not isinstance(value, MutableList):
            if isinstance(value, list):
                return MutableList(value)
            return Mutable.coerce(key, value)
        else:
            return value


class Tags(db.Model):
    name = db.Column(db.String(50), primary_key=True, nullable=False)
    exp_ids = db.Column(MutableList.as_mutable(db.ARRAY(db.INTEGER)))

    def __init__(self, name, exp_ids):
        self.name = name
        self.exp_ids = exp_ids

    def __repr__(self):
        return '<UploadAcct %r>' % self.name

