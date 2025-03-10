from datetime import datetime
import bcrypt
from app import db

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    contacts = db.relationship('Contact', backref='owner', lazy=True, cascade='all, delete-orphan')
    groups = db.relationship('Group', backref='owner', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, email, password):
        self.email = email
        self.password = self._hash_password(password)
    
    def _hash_password(self, password):
        if isinstance(password, str):
            password = password.encode('utf-8')
        return bcrypt.hashpw(password, bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        if isinstance(password, str):
            password = password.encode('utf-8')
        return bcrypt.checkpw(password, self.password.encode('utf-8'))
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'created_at': self.created_at.isoformat()
        } 