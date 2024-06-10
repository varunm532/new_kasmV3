""" database dependencies to support sqliteDB examples """
from random import randrange
from datetime import date
import os, base64
import json

from flask_login import UserMixin

from __init__ import app, db
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash


''' Tutorial: https://www.sqlalchemy.org/library.html#tutorials, try to get into Python shell and follow along '''

# Define the Post class to manage actions in 'posts' table,  with a relationship to 'users' table
class Classes(db.Model):
    __tablename__ = 'classes'

    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    csp = db.Column(db.Boolean, default=False)
    csa = db.Column(db.Boolean, default=False)
    robotics = db.Column(db.Boolean, default=False)
    animation = db.Column(db.Boolean, default=False)

    # Constructor
    def __init__(self, user_id, csp=False, csa=False, robotics=False, animation=False):
        self.id = user_id
        self.csp = csp
        self.csa = csa
        self.robotics = robotics
        self.animation = animation

    # String representation of the Classes object
    def __repr__(self):
        return f"Classes(user_id={self.id}, csp={self.csp}, csa={self.csa}, robotics={self.robotics}, animation={self.animation})"

    # CRUD create
    def create(self):
        try:
            db.session.add(self)
            db.session.commit()
            return self
        except IntegrityError:
            db.session.rollback()
            return None

    # CRUD read
    def read(self):
        return {
            "id": self.id,
            "csp": self.csp,
            "csa": self.csa,
            "robotics": self.robotics,
            "animation": self.animation
        }



# Define the User class to manage actions in the 'users' table
# -- Object Relational Mapping (ORM) is the key concept of SQLAlchemy
# -- a.) db.Model is like an inner layer of the onion in ORM
# -- b.) User represents data we want to store, something that is built on db.Model
# -- c.) SQLAlchemy ORM is layer on top of SQLAlchemy Core, then SQLAlchemy engine, SQL
class User(db.Model, UserMixin):
    __tablename__ = 'users'  # table name is plural, class name is singular

    # Define the User schema with "vars" from object
    id = db.Column(db.Integer, primary_key=True)
    _name = db.Column(db.String(255), unique=False, nullable=False)
    _uid = db.Column(db.String(255), unique=True, nullable=False)
    _password = db.Column(db.String(255), unique=False, nullable=False)
    _role = db.Column(db.String(20), default="User", nullable=False)
    kasm_server_needed = db.Column(db.Boolean, default=False)
    status = db.Column(db.Boolean, default=True)

    # Defines a one-to-one relationship with Classes table
    classes = db.relationship("Classes", uselist=False, backref="user", cascade="all, delete")

    # Constructor of a User object, initializes the instance variables within object (self)
    def __init__(self, name, uid, password="123qwerty", kasm_server_needed=False, status=True, role="User"):
        self._name = name
        self._uid = uid
        self.set_password(password)
        self.kasm_server_needed = kasm_server_needed
        self.status = status
        self._role = role

    # UserMixin/Flask-Login require a get_id method to return the id as a string
    def get_id(self):
        return str(self.id)

    # UserMixin/Flask-Login requires is_authenticated to be defined
    @property
    def is_authenticated(self):
        return True

    # UserMixin/Flask-Login requires is_active to be defined
    @property
    def is_active(self):
        return True

    # UserMixin/Flask-Login requires is_anonymous to be defined
    @property
    def is_anonymous(self):
        return False

    # a name getter method, extracts name from object
    @property
    def name(self):
        return self._name

    # a setter function, allows name to be updated after initial object creation
    @name.setter
    def name(self, name):
        self._name = name

    # a getter method, extracts email from object
    @property
    def uid(self):
        return self._uid

    # a setter function, allows name to be updated after initial object creation
    @uid.setter
    def uid(self, uid):
        self._uid = uid

    # check if uid parameter matches user id in object, return boolean
    def is_uid(self, uid):
        return self._uid == uid

    @property
    def password(self):
        return self._password[0:10] + "..."  # because of security only show 1st characters

    # update password, this is conventional setter
    def set_password(self, password):
        """Create a hashed password."""
        self._password = generate_password_hash(password, "pbkdf2:sha256", salt_length=10)

    # check password parameter versus stored/encrypted password
    def is_password(self, password):
        """Check against hashed password."""
        result = check_password_hash(self._password, password)
        return result

    # output content using str(object) in human readable form, uses getter
    # output content using json dumps, this is ready for API response
    def __str__(self):
        return json.dumps(self.read())

    @property
    def role(self):
        return self._role

    @role.setter
    def role(self, role):
        self._role = role

    def is_admin(self):
        return self._role == "Admin"

    # CRUD create/add a new record to the table
    # returns self or None on error
    def create(self):
        try:
            db.session.add(self)  # add prepares to persist person object to Users table
            db.session.commit()  # SqlAlchemy "unit of work pattern" requires a manual commit
            return self
        except IntegrityError:
            db.session.rollback()
            return None

    # CRUD read converts self to dictionary
    # returns dictionary
    def read(self):
        return {
            "id": self.id,
            "name": self.name,
            "uid": self.uid,
            "role": self._role,
            "kasm_server_needed": self.kasm_server_needed,
            "status": self.status,
            "classes": self.classes.read() if self.classes else None
        }

    # CRUD update: updates user name, password, phone
    # returns self
    def update(self, name="", uid="", password="", kasm_server_needed=None, status=None):
        """only updates values with length"""
        if len(name) > 0:
            self.name = name
        if len(uid) > 0:
            self.uid = uid
        if len(password) > 0:
            self.set_password(password)
        if kasm_server_needed is not None:
            self.kasm_server_needed = kasm_server_needed
        if status is not None:
            self.status = status
        db.session.commit()
        return self

    # CRUD delete: remove self
    # None
    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return None

"""Database Creation and Testing """


# Builds working data for testing
def initUsers():
    with app.app_context():
        """Create database and tables"""
        db.create_all()
        """Tester data for table"""
        u1 = User(name='Thomas Edison', uid='toby', password='123toby', kasm_server_needed=True, status=True, role="Admin")
        u2 = User(name='Nicholas Tesla', uid='niko', password='123niko', kasm_server_needed=False, status=True)
        u3 = User(name='Alexander Graham Bell', uid='lex', kasm_server_needed=True, status=True)
        u4 = User(name='Grace Hopper', uid='hop', password='123hop', kasm_server_needed=False, status=True)
        users = [u1, u2, u3, u4]

        """Builds sample user/classes data"""
        for user in users:
            try:
                user.create()
                classes = Classes(user_id=user.id, csp=True, csa=False, robotics=True, animation=False)
                classes.create()
            except IntegrityError:
                db.session.rollback()
                print(f"Records exist, duplicate uid, or error: {user.uid}")
