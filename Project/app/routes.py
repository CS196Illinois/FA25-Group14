from __future__ import annotations

import csv
import re
from functools import lru_cache
from pathlib import Path
from typing import Dict, List
from werkzeug.security import generate_password_hash, check_password_hash

from flask import Blueprint, json, jsonify, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from google import genai
from google.genai import types
import os
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from pip._vendor import cachecontrol
import requests

from app.models import db, User, Review, UserRequirements
from app.forms import LoginForm, RegisterForm, ReviewForm, EditReviewForm

from datetime import datetime

bp = Blueprint('main', __name__)

DATA_PATH = Path(__file__).resolve().parent / 'all_courses.csv'
_GENED_SPLIT = re.compile(r'[;,]')

# Google OAuth Configuration
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
GOOGLE_DISCOVERY_URL = os.environ.get(
    "GOOGLE_DISCOVERY_URL",
    "https://accounts.google.com/.well-known/openid-configuration"
)


def get_google_provider_cfg():
    """Get Google's OAuth 2.0 provider configuration."""
    return requests.get(GOOGLE_DISCOVERY_URL).json()


def get_or_create_user_from_google(user_info):
    """
    Get or create a user from Google OAuth profile.
    Only allows @illinois.edu email addresses.
    Returns (user, error_message) tuple.
    """
    email = user_info.get("email")
    name = user_info.get("name")

    # Verify Illinois email
    if not email or not email.endswith("@illinois.edu"):
        return None, "Only @illinois.edu email addresses are allowed to register."

    # Check if user exists
    user = User.query.filter_by(email=email.lower()).first()

    if user:
        return user, None

    # Create new user (no password needed for OAuth users)
    user = User(
        email=email.lower(),
        name=name or email.split("@")[0],
        password_hash=""  # OAuth users don't need password
    )
    db.session.add(user)
    db.session.commit()

    return user, None


CourseRecord = Dict[str, str]

# lru_cache decorated from ChatGPT suggestion
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


# Google OAuth routes
@bp.route('/login/google')
def google_login():
    """Initiate Google OAuth login flow."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    # Get Google's authorization endpoint
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Construct the OAuth request URI
    request_uri = (
        f"{authorization_endpoint}?"
        f"response_type=code&"
        f"client_id={GOOGLE_CLIENT_ID}&"
        f"redirect_uri={request.url_root}login/google/callback&"
        f"scope=openid email profile&"
        f"access_type=offline&"
        f"prompt=select_account"
    )

    return redirect(request_uri)


@bp.route('/login/google/callback')
def google_callback():
    """Handle Google OAuth callback."""
    # Get authorization code from Google
    code = request.args.get("code")

    if not code:
        flash('Authentication failed. Please try again.', 'error')
        return redirect(url_for('main.login'))

    # Get Google's token endpoint
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    # Exchange authorization code for tokens
    token_url = token_endpoint
    token_data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": request.url_root + "login/google/callback",
        "grant_type": "authorization_code",
    }

    token_response = requests.post(token_url, data=token_data)

    if token_response.status_code != 200:
        flash('Failed to authenticate with Google. Please try again.', 'error')
        return redirect(url_for('main.login'))

    tokens = token_response.json()
    id_token_jwt = tokens.get("id_token")

    # Verify and decode the ID token
    try:
        user_info = id_token.verify_oauth2_token(
            id_token_jwt,
            google_requests.Request(),
            GOOGLE_CLIENT_ID
        )
    except ValueError:
        flash('Invalid authentication token. Please try again.', 'error')
        return redirect(url_for('main.login'))

    # Verify email is verified by Google
    if not user_info.get("email_verified"):
        flash('Your email is not verified by Google. Please verify your email first.', 'error')
        return redirect(url_for('main.login'))

    # Get or create user (only allows @illinois.edu emails)
    user, error = get_or_create_user_from_google(user_info)

    if error:
        flash(error, 'error')
        return redirect(url_for('main.login'))

    # Log the user in
    login_user(user, remember=True)

    # Check if this is a new user
    if user.created_at and (datetime.utcnow() - user.created_at).total_seconds() < 10:
        flash('Welcome to Course Compass! Your account has been created.', 'success')
    else:
        flash('Welcome back!', 'success')

    next_page = request.args.get('next')
    if not next_page or not next_page.startswith('/'):
        next_page = url_for('main.index')

    return redirect(next_page)


# Review routes
@bp.route('/course/<course_code>/review', methods=['GET', 'POST'])
@login_required
def add_review(course_code):

    
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

@bp.route('/api/ai-assistant', methods=['POST'])
def ai_assistant():
    """Generate course recommendations using Gemini AI"""
    

    try:

        client = genai.Client()
        # Get form data
        data = request.get_json()
        major = data.get('major', '')
        goals = data.get('goals', '')
        priorities = data.get('priorities', [])
        
        if not major or not goals:
            return jsonify({'error': 'Major and goals are required'}), 400
        
        # Configure Gemini
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            return jsonify({'error': 'Gemini API key not configured'}), 500
        
        model = "gemini-2.5-flash"
        
        # Get course data for context
        courses = _load_courses()
        
        # Build course context (limit to relevant departments)
        course_context = ""

        prompt_get_course_codes = r"""Given the user's major and interests, recommend 3 course codes available at UIUC that would match those interests. Output Format:
Output ONLY three comma separated course codes in this format:
AAS,CS,MATH
DO NOT include any extra text
"""

        response = client.models.generate_content(model = model, contents = prompt_get_course_codes)
        course_codes: list[str] = response.text.split(',')
        courses = list(filter(lambda c: c['department'] in course_codes, courses))
        if courses:
            # Sample some courses to provide context
            sample_courses = courses  # Limit to avoid token limits
            course_context = "\n".join([
                f"- {c['course_code']}: {c['course_name']} ({c['credit_hours']} hrs) - {c['gen_ed_requirements']}"
                for c in sample_courses if c['course_code'] and c['course_name']
            ])

            
        
        # Build the prompt
        priorities_text = ", ".join(priorities) if priorities else "No specific priorities"
        user_info = f"""
        Major: {major}
        Goals/Interests: {goals}
        Priorities: {priorities_text}
        """

        prompt = f"""
        User Information:
        {user_info}

        Available Courses:
        {course_context}
        """ + r"""

You are an AI course advisor for UIUC students. 

Your job is to recommend 3-4 courses the student should consider given their academic information and a list of available courses.

Primary goal:
Help the student choose Gen-Ed courses that 1) fulfill their remaining Gen-Ed requirements 2) match their personal interests

How to recommend courses:
-FIRST, focus on Gen-Ed needs
-Among Gen-Ed courses, choose those that match the student’s interests
-Avoid recommending courses the student has already taken or is currently taking
-Make sure prerequisites are satisfied
-If the student has few/no Gen-Ed needs or there is a strong match with interests/goals, optimally include major related or elective courses
-For each recommended course, give a short reason

Output Format:
Output ONLY valid JSON in this format:
{
  "recommended_courses": [
    {
      "course": "COURSE_CODE",
      "reason": "Short reason here"
    }
  ]
}

DO NOT include any extra text outside the JSON.
DO NOT wrap the JSON in markdown (no ```).
ONLY output the JSON object.



Example Output:
{
  "recommended_courses": [
    {
      "course": "PHIL 202",
      "reason": "Fulfills Humanities Gen-Ed and matches interest in philosophy"
    },
    {
      "course": "STAT 200",
      "reason": "Fulfills Quantitative Reasoning Gen-Ed and aligns with interest in data"
    },
    {
      "course": "CS 225",
      "reason": "Core CS course and useful next step in the major"
    }
  ]
}
"""

        # Generate response
        response = client.models.generate_content(model = model, contents = prompt)
        response = json.loads(response.text)
        return jsonify({
            'success': True,
            'recommendation': response
        })
        
    except Exception as e:
        print(f"Error in AI assistant: {str(e)}")
        return jsonify({
            'error': f'Failed to generate recommendation: {str(e)}'
        }), 500

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