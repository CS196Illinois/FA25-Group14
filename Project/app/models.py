from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationship to reviews
    reviews = db.relationship('Review', backref='author', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    @property
    def is_illinois_email(self):
        return self.email.endswith('@illinois.edu')

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_code = db.Column(db.String(20), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Review content
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    difficulty = db.Column(db.Integer, nullable=False)  # 1-5 difficulty
    workload = db.Column(db.Integer, nullable=False)  # 1-5 workload
    title = db.Column(db.String(200), nullable=False)
    comment = db.Column(db.Text, nullable=False)
    
    # Metadata
    semester_taken = db.Column(db.String(20))  # e.g., "Fall 2024"
    professor = db.Column(db.String(100))
    grade_received = db.Column(db.String(10))  # e.g., "A", "B+", etc.
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Moderation
    is_flagged = db.Column(db.Boolean, default=False)
    is_approved = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<Review {self.course_code} by {self.author.name}>'
    
    @property
    def rating_stars(self):
        return '★' * self.rating + '☆' * (5 - self.rating)
    
    @property
    def difficulty_text(self):
        levels = {1: 'Very Easy', 2: 'Easy', 3: 'Moderate', 4: 'Hard', 5: 'Very Hard'}
        return levels.get(self.difficulty, 'Unknown')
    
    @property
    def workload_text(self):
        levels = {1: 'Very Light', 2: 'Light', 3: 'Moderate', 4: 'Heavy', 5: 'Very Heavy'}
        return levels.get(self.workload, 'Unknown')
    
    @property
    def time_ago(self):
        now = datetime.utcnow()
        diff = now - self.created_at
        
        if diff.days > 365:
            years = diff.days // 365
            return f"{years} year{'s' if years > 1 else ''} ago"
        elif diff.days > 30:
            months = diff.days // 30
            return f"{months} month{'s' if months > 1 else ''} ago"
        elif diff.days > 0:
            return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        else:
            return "Just now"