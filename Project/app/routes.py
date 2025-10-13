from __future__ import annotations

import csv
import re
from functools import lru_cache
from pathlib import Path
from typing import Dict, List
from werkzeug.security import generate_password_hash, check_password_hash

from flask import Blueprint, jsonify, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user

from datetime import datetime
from app.models import db, UserRequirements

bp = Blueprint('main', __name__)

DATA_PATH = Path(__file__).resolve().parent / 'all_courses.csv'
_GENED_SPLIT = re.compile(r'[;,]')


CourseRecord = Dict[str, str]


@lru_cache(maxsize=1)
def _load_courses() -> List[CourseRecord]:
    courses: List[CourseRecord] = []
    if not DATA_PATH.exists():
        return courses

    with DATA_PATH.open('r', encoding='utf-8-sig', newline='') as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            courses.append({
                'course_code': row.get('course_code', '').strip(),
                'course_name': row.get('course_name', '').strip(),
                'credit_hours': row.get('credit_hours', '').strip(),
                'department': row.get('department', '').strip(),
                'gen_ed_requirements': row.get('gen_ed_requirements', '').strip(),
                'description': row.get('description', '').strip(),
            })
    
    return courses


@bp.route('/api/courses/meta')
def courses_meta():
    courses = _load_courses()
    departments = sorted({course['department'] for course in courses if course['department']})
    geneds = sorted({
        part.strip()
        for course in courses
        for part in _GENED_SPLIT.split(course['gen_ed_requirements'])
        if part.strip()
    })
    return jsonify({'departments': departments, 'geneds': geneds})


@bp.route('/api/courses')
def api_courses():
    courses = _load_courses()
    if not courses:
        return jsonify({'results': [], 'matches': 0, 'limit': 0})

    department = request.args.get('major', default='all').strip() or 'all'
    geneds_param = request.args.get('geneds', default='').strip()
    required_geneds = [g.strip() for g in geneds_param.split(',') if g.strip()] if geneds_param else []
    query = request.args.get('q', default='').strip().lower()

    limit = min(max(request.args.get('limit', default=30, type=int), 1), 120)

    def matches(course: CourseRecord) -> bool:
        if department != 'all' and course['department'] != department:
            return False
        if required_geneds:
            course_geneds = [
                part.strip()
                for part in _GENED_SPLIT.split(course['gen_ed_requirements'])
                if part.strip()
            ]
            # Course must have ALL required gen eds
            for required_gened in required_geneds:
                # Special case for combined Humanities requirement
                if required_gened == 'Humanities':
                    humanities_found = any(
                        gened in ['Humanities - Hist & Phil', 'Humanities - Lit & Arts']
                        for gened in course_geneds
                    )
                    if not humanities_found:
                        return False
                else:
                    if required_gened not in course_geneds:
                        return False
        if query:
            haystack = f"{course['course_code']} {course['course_name']} {course['description']}".lower()
            if query not in haystack:
                return False
        return True

    filtered = [course for course in courses if matches(course)]
    
    # Sort by search relevance if there's a query
    if query:
        def get_search_score(course: CourseRecord) -> int:
            """Calculate search relevance score (higher = more relevant)"""
            score = 0
            course_code_lower = course['course_code'].lower()
            course_name_lower = course['course_name'].lower()
            
            # Highest priority: exact match in course code
            if query == course_code_lower:
                score += 1000
            # High priority: query starts course code
            elif course_code_lower.startswith(query):
                score += 800
            # Medium-high priority: query in course code
            elif query in course_code_lower:
                score += 600
                
            # High priority: exact match in course name
            if query == course_name_lower:
                score += 900
            # Medium-high priority: query starts course name
            elif course_name_lower.startswith(query):
                score += 700
            # Medium priority: query in course name
            elif query in course_name_lower:
                score += 500
                
            # Lower priority: query in description
            if query in course['description'].lower():
                score += 100
                
            return score
        
        filtered.sort(key=get_search_score, reverse=True)
    
    limited = filtered[:limit]

    return jsonify(
        {
            'results': limited,
            'matches': len(filtered),
            'limit': limit,
        }
    )

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/course/<course_code>')
def course_detail(course_code):
    from app.models import Review
    from flask_login import current_user
    
    courses = _load_courses()
    course = next((c for c in courses if c['course_code'] == course_code), None)
    
    if not course:
        return render_template('404.html', course_code=course_code), 404
    
    # Find related courses in same department
    related_courses = [
        c for c in courses 
        if c['department'] == course['department'] and c['course_code'] != course_code
    ][:6]  # Limit to 6 related courses
    
    # Get reviews for this course
    reviews = Review.query.filter_by(
        course_code=course_code, 
        is_approved=True
    ).order_by(Review.created_at.desc()).all()
    
    # Calculate average ratings
    avg_rating = 0
    avg_difficulty = 0
    avg_workload = 0
    
    if reviews:
        avg_rating = sum(r.rating for r in reviews) / len(reviews)
        avg_difficulty = sum(r.difficulty for r in reviews) / len(reviews)
        avg_workload = sum(r.workload for r in reviews) / len(reviews)
    
    # Check if current user has already reviewed this course
    user_review = None
    if current_user.is_authenticated:
        user_review = Review.query.filter_by(
            course_code=course_code,
            user_id=current_user.id
        ).first()
    
    return render_template('course_detail.html', 
                         course=course, 
                         related_courses=related_courses,
                         reviews=reviews,
                         avg_rating=avg_rating,
                         avg_difficulty=avg_difficulty,
                         avg_workload=avg_workload,
                         user_review=user_review)

# Authentication routes
@bp.route('/login', methods=['GET', 'POST'])
def login():
    from app.forms import LoginForm
    from app.models import User, db
    
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=True)
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('main.index')
            flash('Welcome back!', 'success')
            return redirect(next_page)
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('auth/login.html', form=form)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    from app.forms import RegisterForm
    from app.models import User, db
    
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        # Check if user already exists
        existing_user = User.query.filter_by(email=form.email.data.lower()).first()
        if existing_user:
            flash('An account with this email already exists', 'error')
            return render_template('auth/register.html', form=form)
        
        # Create new user
        user = User(
            name=form.name.data,
            email=form.email.data.lower(),
            password_hash=generate_password_hash(form.password.data)
        )
        db.session.add(user)
        db.session.commit()
        
        login_user(user, remember=True)
        flash('Welcome to Course Compass! Your account has been created.', 'success')
        return redirect(url_for('main.index'))
    
    return render_template('auth/register.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('main.index'))

# Review routes
@bp.route('/course/<course_code>/review', methods=['GET', 'POST'])
@login_required
def add_review(course_code):
    from app.forms import ReviewForm
    from app.models import Review, db
    
    courses = _load_courses()
    course = next((c for c in courses if c['course_code'] == course_code), None)
    
    if not course:
        flash('Course not found', 'error')
        return redirect(url_for('main.index'))
    
    # Check if user already reviewed this course
    existing_review = Review.query.filter_by(
        course_code=course_code,
        user_id=current_user.id
    ).first()
    
    if existing_review:
        flash('You have already reviewed this course. You can edit your existing review.', 'info')
        return redirect(url_for('main.edit_review', course_code=course_code))
    
    form = ReviewForm()
    if form.validate_on_submit():
        review = Review(
            course_code=course_code,
            user_id=current_user.id,
            rating=int(form.rating.data),
            difficulty=int(form.difficulty.data),
            workload=int(form.workload.data),
            title=form.title.data,
            comment=form.comment.data,
            semester_taken=form.semester_taken.data or None,
            professor=form.professor.data or None,
            grade_received=form.grade_received.data or None
        )
        db.session.add(review)
        db.session.commit()
        
        flash('Your review has been submitted! Thank you for helping other students.', 'success')
        return redirect(url_for('main.course_detail', course_code=course_code))
    
    return render_template('reviews/add_review.html', form=form, course=course)

@bp.route('/course/<course_code>/review/edit', methods=['GET', 'POST'])
@login_required
def edit_review(course_code):
    from app.forms import EditReviewForm
    from app.models import Review, db
    
    review = Review.query.filter_by(
        course_code=course_code,
        user_id=current_user.id
    ).first()
    
    if not review:
        flash('Review not found', 'error')
        return redirect(url_for('main.course_detail', course_code=course_code))
    
    courses = _load_courses()
    course = next((c for c in courses if c['course_code'] == course_code), None)
    
    form = EditReviewForm(obj=review)
    if form.validate_on_submit():
        form.populate_obj(review)
        review.rating = int(form.rating.data)
        review.difficulty = int(form.difficulty.data) 
        review.workload = int(form.workload.data)
        db.session.commit()
        
        flash('Your review has been updated', 'success')
        return redirect(url_for('main.course_detail', course_code=course_code))
    
    return render_template('reviews/edit_review.html', form=form, course=course, review=review)

@bp.route('/course/<course_code>/review/delete', methods=['POST'])
@login_required
def delete_review(course_code):
    from app.models import Review, db
    
    review = Review.query.filter_by(
        course_code=course_code,
        user_id=current_user.id
    ).first()
    
    if review:
        db.session.delete(review)
        db.session.commit()
        flash('Your review has been deleted', 'info')
    else:
        flash('Review not found', 'error')
    
    return redirect(url_for('main.course_detail', course_code=course_code))

@bp.route('/hello')
def hello():
    return 'Hello, Flask!'

# Dashboard routes
@bp.route('/dashboard')
@login_required
def dashboard():
    from app.forms import PasswordUpdateForm, AuditUploadForm
    
    # Get or create user requirements
    requirements = UserRequirements.query.filter_by(user_id=current_user.id).first()
    if not requirements:
        requirements = UserRequirements(user_id=current_user.id)
        db.session.add(requirements)
        db.session.commit()
    
    password_form = PasswordUpdateForm()
    audit_form = AuditUploadForm()
    
    return render_template('dashboard/dashboard.html', 
                         requirements=requirements,
                         password_form=password_form,
                         audit_form=audit_form)

@bp.route('/upload_audit', methods=['POST'])
@login_required
def upload_audit():
    from app.forms import AuditUploadForm
    from app.utils.pdf_parser import DegreeAuditParser
    from app.models import UserRequirements
    
    form = AuditUploadForm()
    requirements = UserRequirements.query.filter_by(user_id=current_user.id).first()
    
    if form.validate_on_submit():
        try:
            # Parse the PDF
            parser = DegreeAuditParser(form.audit_file.data)
            parsed_requirements = parser.parse_requirements()
            
            # Update user requirements
            for key, value in parsed_requirements.items():
                if hasattr(requirements, key):
                    setattr(requirements, key, value)
            
            requirements.audit_uploaded = True
            requirements.last_updated = datetime.utcnow()
            db.session.commit()
            
            flash('Degree audit uploaded and parsed successfully!', 'success')
        except Exception as e:
            flash(f'Error processing PDF: {str(e)}', 'error')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{getattr(form, field).label.text}: {error}', 'error')
    
    return redirect(url_for('main.dashboard'))

@bp.route('/update_password', methods=['POST'])
@login_required
def update_password():
    from app.forms import PasswordUpdateForm
    
    form = PasswordUpdateForm()
    if form.validate_on_submit():
        # Verify current password
        if check_password_hash(current_user.password_hash, form.current_password.data):
            # Update password
            current_user.password_hash = generate_password_hash(form.new_password.data)
            db.session.commit()
            flash('Your password has been updated successfully!', 'success')
        else:
            flash('Current password is incorrect', 'error')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{getattr(form, field).label.text}: {error}', 'error')
    
    return redirect(url_for('main.dashboard'))

@bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    from app.forms import PasswordUpdateForm
    
    form = PasswordUpdateForm()
    
    if form.validate_on_submit():
        # Verify current password
        if check_password_hash(current_user.password_hash, form.current_password.data):
            # Update password
            current_user.password_hash = generate_password_hash(form.new_password.data)
            db.session.commit()
            flash('Your password has been updated successfully!', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Current password is incorrect', 'error')
    
    return render_template('auth/change_password.html', form=form)