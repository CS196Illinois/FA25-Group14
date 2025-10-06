from flask import Blueprint, redirect, url_for, request, session, jsonify, render_template, flash
from flask_login import login_required, current_user
import requests
import secrets

from app.canvas.config import CanvasConfig
from app.canvas.service import CanvasService
from app.canvas.models import CanvasToken
from app.models import db

canvas_bp = Blueprint('canvas', __name__)

@canvas_bp.route('/canvas/connect')
@login_required
def connect_canvas():
    """Redirect to Canvas authorization page"""
    if not CanvasConfig.is_configured():
        flash('Canvas integration is not configured. Please contact administrator.', 'error')
        return redirect(url_for('main.index'))
    
    # Generate state parameter for CSRF protection
    state = secrets.token_urlsafe(16)
    session['canvas_oauth_state'] = state
    
    # Build authorization URL
    auth_url = CanvasConfig.AUTH_URL
    params = {
        'client_id': CanvasConfig.CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': CanvasConfig.REDIRECT_URI,
        'scope': ' '.join(CanvasConfig.SCOPES),
        'state': state
    }
    
    auth_url_with_params = f"{auth_url}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"
    
    # Store authorization context in session for the callback
    session['canvas_authorization_context'] = {
        'purpose': 'import_courses_grades',
        'optional': True
    }
    
    return redirect(auth_url_with_params)

@canvas_bp.route('/canvas/callback')
@login_required
def canvas_callback():
    """Handle Canvas OAuth callback"""
    # Verify state parameter
    state = request.args.get('state')
    if not state or state != session.get('canvas_oauth_state'):
        flash('Invalid OAuth state parameter', 'error')
        return redirect(url_for('main.index'))
    
    # Clear state from session
    session.pop('canvas_oauth_state', None)
    
    code = request.args.get('code')
    error = request.args.get('error')
    
    # Get authorization context
    auth_context = session.get('canvas_authorization_context', {})
    session.pop('canvas_authorization_context', None)
    
    if error:
        if error == 'access_denied' and auth_context.get('optional'):
            flash('Canvas connection was not completed. You can manually enter your course history in your dashboard.', 'info')
            return redirect(url_for('main.index'))
        else:
            flash(f'Canvas authorization failed: {error}', 'error')
            return redirect(url_for('main.index'))
    
    if not code:
        flash('Authorization code not received', 'error')
        return redirect(url_for('main.index'))
    
    try:
        # Exchange for access token
        token_data = {
            'grant_type': 'authorization_code',
            'client_id': CanvasConfig.CLIENT_ID,
            'client_secret': CanvasConfig.CLIENT_SECRET,
            'redirect_uri': CanvasConfig.REDIRECT_URI,
            'code': code
        }
        
        response = requests.post(CanvasConfig.TOKEN_URL, data=token_data)
        
        if response.status_code != 200:
            flash('Failed to obtain access token from Canvas', 'error')
            return redirect(url_for('main.index'))
        
        token_info = response.json()
        
        if 'access_token' in token_info:
            # Check if token already exists
            existing_token = CanvasToken.query.filter_by(user_id=current_user.id).first()
            
            if existing_token:
                # Update existing token
                existing_token.access_token = token_info['access_token']
                existing_token.refresh_token = token_info.get('refresh_token')
                existing_token.expires_in = token_info.get('expires_in')
            else:
                # Create new token
                canvas_token = CanvasToken(
                    user_id=current_user.id,
                    access_token=token_info['access_token'],
                    refresh_token=token_info.get('refresh_token'),
                    expires_in=token_info.get('expires_in')
                )
                db.session.add(canvas_token)
            
            db.session.commit()
            
            # Import course and grade data
            canvas_service = CanvasService(token_info['access_token'])
            courses_with_grades = canvas_service.get_courses_with_grades()
            
            if courses_with_grades:
                # Store course data in user session or database (simplified example)
                session['imported_courses'] = courses_with_grades
                course_count = len(courses_with_grades)
                flash(f'Successfully imported {course_count} courses with grade information from Canvas!', 'success')
            else:
                flash('Canvas account connected, but no course data was found.', 'info')
                
        else:
            flash('Failed to obtain access token from Canvas', 'error')
            
    except Exception as e:
        flash(f'Canvas connection failed: {str(e)}', 'error')
        print(f"Canvas OAuth error: {e}")
    
    return redirect(url_for('main.index'))

@canvas_bp.route('/canvas/disconnect', methods=['POST'])
@login_required
def disconnect_canvas():
    """Disconnect Canvas integration"""
    try:
        canvas_token = CanvasToken.query.filter_by(user_id=current_user.id).first()
        if canvas_token:
            db.session.delete(canvas_token)
            db.session.commit()
            # Clear imported course data from session
            session.pop('imported_courses', None)
            flash('Canvas account disconnected successfully', 'success')
        else:
            flash('No Canvas connection found', 'info')
    except Exception as e:
        flash(f'Failed to disconnect Canvas: {str(e)}', 'error')
    
    return redirect(url_for('main.index'))

@canvas_bp.route('/api/canvas/courses-grades')
@login_required
def api_canvas_courses_grades():
    """API endpoint: Get Canvas courses with grades"""
    try:
        canvas_token = CanvasToken.query.filter_by(user_id=current_user.id).first()
        if not canvas_token:
            return jsonify({'success': False, 'error': 'No Canvas connection found'}), 401
        
        canvas_service = CanvasService(canvas_token.access_token)
        courses_grades = canvas_service.get_courses_with_grades()
        
        if courses_grades is not None:
            return jsonify({'success': True, 'courses_grades': courses_grades})
        else:
            return jsonify({'success': False, 'error': 'Failed to fetch courses and grades from Canvas'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@canvas_bp.route('/canvas/import-courses')
@login_required
def import_courses_page():
    """Page to import courses from Canvas"""
    canvas_token = CanvasToken.query.filter_by(user_id=current_user.id).first()
    has_canvas_connection = canvas_token is not None
    
    # Get imported courses from session if available
    imported_courses = session.get('imported_courses', [])
    
    return render_template('canvas/import_courses.html', 
                         has_canvas_connection=has_canvas_connection,
                         imported_courses=imported_courses)