from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False) # Increased length for stronger hashes
    orcid_id = db.Column(db.String(50), unique=True, nullable=True) # ORCID can be optional in general, but required on reg
    user_type = db.Column(db.String(20), nullable=False) # 'Student' or 'Faculty'
    
    papers = db.relationship('Paper', backref='author_user', lazy=True)
    orcid_works = db.relationship('OrcidWork', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class Paper(db.Model):
    __tablename__ = 'papers'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author_name = db.Column(db.String(200), nullable=False) # 'Author' field from form
    category = db.Column(db.String(50), nullable=False) # Journal / Conference / Book Chapter
    publication_name = db.Column(db.String(200), nullable=False) # Name of Journal/Conf/Book
    publication_date = db.Column(db.Date, nullable=False)
    file_path = db.Column(db.String(300), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return f'<Paper {self.title}>'

class OrcidWork(db.Model):
    __tablename__ = 'orcid_data'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    put_code = db.Column(db.String(50), nullable=True) # ORCID internal identifier for the work
    title = db.Column(db.String(500), nullable=True)
    work_type = db.Column(db.String(100), nullable=True)
    publication_year = db.Column(db.String(10), nullable=True)
    journal_title = db.Column(db.String(300), nullable=True)
    doi = db.Column(db.String(100), nullable=True) # Digital Object Identifier

    def __repr__(self):
        return f'<OrcidWork {self.title} for User ID {self.user_id}>'