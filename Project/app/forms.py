from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email, NumberRange, ValidationError
from wtforms.widgets import TextArea
import re

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Please enter a valid email address')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required'),
        Length(min=6, message='Password must be at least 6 characters')
    ])
    submit = SubmitField('Log In')
    
    def validate_email(self, field):
        if not field.data.endswith('@illinois.edu'):
            raise ValidationError('Please use your @illinois.edu email address')

class RegisterForm(FlaskForm):
    name = StringField('Full Name', validators=[
        DataRequired(message='Name is required'),
        Length(min=2, max=100, message='Name must be between 2 and 100 characters')
    ])
    email = StringField('Illinois Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Please enter a valid email address')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required'),
        Length(min=6, message='Password must be at least 6 characters')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(message='Please confirm your password')
    ])
    submit = SubmitField('Create Account')
    
    def validate_email(self, field):
        if not field.data.endswith('@illinois.edu'):
            raise ValidationError('Please use your @illinois.edu email address')
    
    def validate_confirm_password(self, field):
        if field.data != self.password.data:
            raise ValidationError('Passwords must match')

class ReviewForm(FlaskForm):
    # Basic review info
    title = StringField('Review Title', validators=[
        DataRequired(message='Please provide a title for your review'),
        Length(min=5, max=200, message='Title must be between 5 and 200 characters')
    ])
    
    rating = SelectField('Overall Rating', 
        choices=[
            ('5', '★★★★★ Excellent'),
            ('4', '★★★★☆ Good'), 
            ('3', '★★★☆☆ Average'),
            ('2', '★★☆☆☆ Poor'),
            ('1', '★☆☆☆☆ Terrible')
        ],
        validators=[DataRequired(message='Please select a rating')]
    )
    
    difficulty = SelectField('Difficulty Level',
        choices=[
            ('1', '1 - Very Easy'),
            ('2', '2 - Easy'),
            ('3', '3 - Moderate'), 
            ('4', '4 - Hard'),
            ('5', '5 - Very Hard')
        ],
        validators=[DataRequired(message='Please select difficulty level')]
    )
    
    workload = SelectField('Workload',
        choices=[
            ('1', '1 - Very Light (< 3 hrs/week)'),
            ('2', '2 - Light (3-6 hrs/week)'),
            ('3', '3 - Moderate (6-10 hrs/week)'),
            ('4', '4 - Heavy (10-15 hrs/week)'),
            ('5', '5 - Very Heavy (15+ hrs/week)')
        ],
        validators=[DataRequired(message='Please select workload level')]
    )
    
    comment = TextAreaField('Your Review', 
        validators=[
            DataRequired(message='Please write your review'),
            Length(min=50, max=2000, message='Review must be between 50 and 2000 characters')
        ],
        render_kw={
            'rows': 6, 
            'placeholder': 'Share your experience with this course. What did you like? What was challenging? Any tips for future students?'
        }
    )
    
    # Optional additional info
    semester_taken = SelectField('Semester Taken (Optional)',
        choices=[
            ('', 'Select semester...'),
            ('Fall 2024', 'Fall 2024'),
            ('Spring 2024', 'Spring 2024'), 
            ('Summer 2024', 'Summer 2024'),
            ('Fall 2023', 'Fall 2023'),
            ('Spring 2023', 'Spring 2023'),
            ('Summer 2023', 'Summer 2023'),
            ('Fall 2022', 'Fall 2022'),
            ('Spring 2022', 'Spring 2022'),
            ('Other', 'Other/Earlier')
        ]
    )
    
    professor = StringField('Professor (Optional)', 
        validators=[Length(max=100)],
        render_kw={'placeholder': 'e.g., Dr. Smith'}
    )
    
    grade_received = SelectField('Grade Received (Optional)',
        choices=[
            ('', 'Select grade...'),
            ('A+', 'A+'), ('A', 'A'), ('A-', 'A-'),
            ('B+', 'B+'), ('B', 'B'), ('B-', 'B-'), 
            ('C+', 'C+'), ('C', 'C'), ('C-', 'C-'),
            ('D+', 'D+'), ('D', 'D'), ('D-', 'D-'),
            ('F', 'F'), ('W', 'W (Withdrew)'), ('P', 'P (Pass)'),
            ('CR', 'CR (Credit)'), ('NC', 'NC (No Credit)')
        ]
    )
    
    submit = SubmitField('Submit Review')
    
    def validate_comment(self, field):
        # Basic content filtering
        inappropriate_words = ['spam', 'test123', 'asdf']  # Add more as needed
        comment_lower = field.data.lower()
        
        for word in inappropriate_words:
            if word in comment_lower:
                raise ValidationError('Please provide a helpful, constructive review')
        
        # Check for minimum word count (roughly 10 words)
        word_count = len(field.data.split())
        if word_count < 10:
            raise ValidationError('Please provide a more detailed review (at least 10 words)')

class EditReviewForm(ReviewForm):
    submit = SubmitField('Update Review')