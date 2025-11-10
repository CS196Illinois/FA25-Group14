import os
from supabase import create_client, Client
from dotenv import load_dotenv
from typing import Optional, List, Dict, Any
from datetime import datetime

load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(supabase_url=url, supabase_key=key)

# ============================================================================
# USER FUNCTIONS
# ============================================================================

def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Get user by email address."""
    try:
        response = supabase.table('user').select('*').eq('email', email).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None
    except Exception as e:
        print(f"Error getting user by email: {e}")
        return None

def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """Get user by ID."""
    try:
        response = supabase.table('user').select('*').eq('id', user_id).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None
    except Exception as e:
        print(f"Error getting user by id: {e}")
        return None

def create_user(name: str, email: str, password_hash: str) -> Optional[Dict[str, Any]]:
    """Create a new user."""
    try:
        data = {
            'name': name,
            'email': email,
            'password_hash': password_hash,
            'created_at': datetime.utcnow().isoformat(),
            'is_active': True
        }
        response = supabase.table('user').insert(data).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None
    except Exception as e:
        print(f"Error creating user: {e}")
        return None

def update_user_password(user_id: int, new_password_hash: str) -> bool:
    """Update user's password."""
    try:
        response = supabase.table('user').update({
            'password_hash': new_password_hash
        }).eq('id', user_id).execute()
        return response.data is not None
    except Exception as e:
        print(f"Error updating user password: {e}")
        return False

# ============================================================================
# REVIEW FUNCTIONS
# ============================================================================

def get_reviews_by_course(course_code: str, approved_only: bool = True) -> List[Dict[str, Any]]:
    """Get all reviews for a specific course."""
    try:
        query = supabase.table('review').select('*, author:user_id(id, name, email)').eq('course_code', course_code)
        
        if approved_only:
            query = query.eq('is_approved', True)
        
        response = query.order('created_at', desc=True).execute()
        return response.data if response.data else []
    except Exception as e:
        print(f"Error getting reviews by course: {e}")
        return []

def get_user_review_for_course(user_id: int, course_code: str) -> Optional[Dict[str, Any]]:
    """Get a user's review for a specific course."""
    try:
        response = supabase.table('review').select('*').eq('user_id', user_id).eq('course_code', course_code).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None
    except Exception as e:
        print(f"Error getting user review: {e}")
        return None

def create_review(course_code: str, user_id: int, rating: int, difficulty: int, 
                 workload: int, title: str, comment: str, semester_taken: Optional[str] = None,
                 professor: Optional[str] = None, grade_received: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Create a new review."""
    try:
        data = {
            'course_code': course_code,
            'user_id': user_id,
            'rating': rating,
            'difficulty': difficulty,
            'workload': workload,
            'title': title,
            'comment': comment,
            'semester_taken': semester_taken,
            'professor': professor,
            'grade_received': grade_received,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat(),
            'is_approved': True,
            'is_flagged': False
        }
        response = supabase.table('review').insert(data).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None
    except Exception as e:
        print(f"Error creating review: {e}")
        return None

def update_review(review_id: int, rating: int, difficulty: int, workload: int,
                 title: str, comment: str, semester_taken: Optional[str] = None,
                 professor: Optional[str] = None, grade_received: Optional[str] = None) -> bool:
    """Update an existing review."""
    try:
        data = {
            'rating': rating,
            'difficulty': difficulty,
            'workload': workload,
            'title': title,
            'comment': comment,
            'semester_taken': semester_taken,
            'professor': professor,
            'grade_received': grade_received,
            'updated_at': datetime.utcnow().isoformat()
        }
        response = supabase.table('review').update(data).eq('id', review_id).execute()
        return response.data is not None
    except Exception as e:
        print(f"Error updating review: {e}")
        return False

def delete_review(review_id: int) -> bool:
    """Delete a review."""
    try:
        response = supabase.table('review').delete().eq('id', review_id).execute()
        return response.data is not None
    except Exception as e:
        print(f"Error deleting review: {e}")
        return False

# ============================================================================
# MESSAGE FUNCTIONS
# ============================================================================

def get_messages_by_course(course_code: str, limit: int = 100) -> List[Dict[str, Any]]:
    """Get messages for a specific course."""
    try:
        response = supabase.table('message').select('*, author:user_id(id, name, email)').eq(
            'course_code', course_code
        ).eq('is_deleted', False).order('created_at', desc=True).limit(limit).execute()
        
        # Reverse to show oldest first
        if response.data:
            return list(reversed(response.data))
        return []
    except Exception as e:
        print(f"Error getting messages: {e}")
        return []

def create_message(course_code: str, user_id: int, content: str) -> Optional[Dict[str, Any]]:
    """Create a new message."""
    try:
        data = {
            'course_code': course_code,
            'user_id': user_id,
            'content': content,
            'created_at': datetime.utcnow().isoformat(),
            'is_flagged': False,
            'is_deleted': False
        }
        response = supabase.table('message').insert(data).execute()
        if response.data and len(response.data) > 0:
            # Get the message with author info
            message_id = response.data[0]['id']
            full_message = supabase.table('message').select('*, author:user_id(id, name, email)').eq('id', message_id).execute()
            if full_message.data and len(full_message.data) > 0:
                return full_message.data[0]
        return None
    except Exception as e:
        print(f"Error creating message: {e}")
        return None

def soft_delete_message(message_id: int) -> bool:
    """Soft delete a message (mark as deleted)."""
    try:
        response = supabase.table('message').update({
            'is_deleted': True
        }).eq('id', message_id).execute()
        return response.data is not None
    except Exception as e:
        print(f"Error deleting message: {e}")
        return False

def get_message_by_id(message_id: int) -> Optional[Dict[str, Any]]:
    """Get a single message by ID."""
    try:
        response = supabase.table('message').select('*').eq('id', message_id).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None
    except Exception as e:
        print(f"Error getting message: {e}")
        return None

# ============================================================================
# USER REQUIREMENTS FUNCTIONS
# ============================================================================

def get_user_requirements(user_id: int) -> Optional[Dict[str, Any]]:
    """Get user requirements/gen-ed progress."""
    try:
        response = supabase.table('user_requirements').select('*').eq('user_id', user_id).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None
    except Exception as e:
        print(f"Error getting user requirements: {e}")
        return None

def create_user_requirements(user_id: int) -> Optional[Dict[str, Any]]:
    """Create new user requirements record."""
    try:
        data = {
            'user_id': user_id,
            'advanced_composition': False,
            'composition1': False,
            'quantitative_reasoning1': False,
            'quantitative_reasoning2': False,
            'western_culture': False,
            'non_western_culture': False,
            'us_minority_culture': False,
            'language_requirement': False,
            'humanities_arts': False,
            'social_behavioral': False,
            'natural_sciences': False,
            'humanities_hp': False,
            'humanities_la': False,
            'social_behavioral_bsc': False,
            'social_behavioral_ss': False,
            'natural_sciences_ls': False,
            'natural_sciences_ps': False,
            'audit_uploaded': False,
            'last_updated': datetime.utcnow().isoformat()
        }
        response = supabase.table('user_requirements').insert(data).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None
    except Exception as e:
        print(f"Error creating user requirements: {e}")
        return None

def update_user_requirements(user_id: int, updates: Dict[str, Any]) -> bool:
    """Update user requirements."""
    try:
        updates['last_updated'] = datetime.utcnow().isoformat()
        response = supabase.table('user_requirements').update(updates).eq('user_id', user_id).execute()
        return response.data is not None
    except Exception as e:
        print(f"Error updating user requirements: {e}")
        return False
    
def get_all_users() -> List[Dict[str, Any]]:
    """Get all users (for admin purposes)."""
    try:
        response = supabase.table('user').select('*').execute()
        return response.data if response.data else []
    except Exception as e:
        print(f"Error getting all users: {e}")
        return []

if __name__ == "__main__":
    # Simple test to verify connection
    print(get_all_users())