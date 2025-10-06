from app.models import db
from datetime import datetime

class CanvasToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    access_token = db.Column(db.Text, nullable=False)
    refresh_token = db.Column(db.Text)
    expires_in = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('canvas_tokens', lazy=True))
    
    def __repr__(self):
        return f'<CanvasToken for User {self.user_id}>'
    
    def is_expired(self):
        """Check if token is expired"""
        if not self.expires_in:
            return False
        expiry_time = self.created_at.timestamp() + self.expires_in
        return datetime.utcnow().timestamp() > expiry_time