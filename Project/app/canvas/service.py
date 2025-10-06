import requests
from flask import current_app
from app.canvas.config import CanvasConfig

class CanvasService:
    def __init__(self, access_token):
        self.access_token = access_token
        self.base_url = CanvasConfig.BASE_URL
        self.headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
    
    def get_courses_with_grades(self):
        """Get user courses with grade information"""
        try:
            # Get all courses (including past courses)
            params = {
                'enrollment_state': 'completed',  # Get completed courses for historical grades
                'include': ['total_scores']
            }
            
            response = requests.get(
                f"{self.base_url}/api/v1/courses",
                headers=self.headers,
                params=params
            )
            
            if response.status_code == 200:
                courses = response.json()
                
                # Extract course and grade information
                course_grades = []
                for course in courses:
                    # Get enrollment information which contains grades
                    enrollment_info = self._get_course_enrollment(course['id'])
                    if enrollment_info:
                        course_grades.append({
                            'course_id': course['id'],
                            'course_name': course.get('name', 'Unnamed Course'),
                            'course_code': course.get('course_code', 'No Code'),
                            'grades': enrollment_info
                        })
                
                return course_grades
            return None
        except Exception as e:
            print(f"Error fetching courses with grades: {e}")
            return None
    
    def _get_course_enrollment(self, course_id):
        """Get enrollment information for a specific course"""
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/courses/{course_id}/enrollments",
                headers=self.headers,
                params={'user_id': 'self'}
            )
            
            if response.status_code == 200:
                enrollments = response.json()
                # Find student enrollment
                for enrollment in enrollments:
                    if enrollment.get('type') == 'StudentEnrollment':
                        return {
                            'current_score': enrollment.get('computed_current_score'),
                            'current_grade': enrollment.get('computed_current_grade'),
                            'final_score': enrollment.get('computed_final_score'),
                            'final_grade': enrollment.get('computed_final_grade'),
                            'enrollment_state': enrollment.get('enrollment_state')
                        }
            return None
        except Exception as e:
            print(f"Error fetching enrollment for course {course_id}: {e}")
            return None
    
    def test_connection(self):
        """Test if connection is valid"""
        courses = self.get_courses_with_grades()
        return courses is not None