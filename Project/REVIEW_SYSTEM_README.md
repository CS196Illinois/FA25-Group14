# Course Review System - Rate My Professor Style

A comprehensive review system allowing UIUC students to rate and review courses, similar to Rate My Professor but focused on course experiences.

## Features

### User Authentication

- **Illinois Email Required**: Only @illinois.edu email addresses can create accounts
- **Secure Registration**: Password hashing with Werkzeug security
- **Session Management**: Flask-Login for user sessions and authentication
- **Login/Logout**: Full authentication flow with redirect handling

### Course Reviews

- **Comprehensive Rating System**:
  - Overall rating (1-5 stars)
  - Difficulty level (1-5 scale)
  - Workload assessment (1-5 scale)
- **Structured Reviews**: Title + detailed comment (minimum 50 characters)
- **Additional Context**: Optional semester, professor, and grade information
- **One Review Per Course**: Users can only review each course once (but can edit)

### Review Management

- **View Reviews**: All approved reviews displayed on course pages
- **Edit Reviews**: Users can update their existing reviews
- **Delete Reviews**: Users can remove their reviews
- **Review Statistics**: Average ratings and statistics per course
- **Content Moderation**: Basic filtering and approval system

### User Interface

- **Responsive Design**: Works on desktop and mobile devices
- **Flash Messages**: User feedback for actions and errors
- **Form Validation**: Client and server-side validation
- **Navigation Integration**: Seamless integration with course explorer

## Database Schema

### Users Table

```sql
CREATE TABLE user (
    id INTEGER PRIMARY KEY,
    email VARCHAR(120) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    password_hash VARCHAR(128),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);
```

### Reviews Table

```sql
CREATE TABLE review (
    id INTEGER PRIMARY KEY,
    course_code VARCHAR(20) NOT NULL,
    user_id INTEGER NOT NULL,
    rating INTEGER NOT NULL,
    difficulty INTEGER NOT NULL,
    workload INTEGER NOT NULL,
    title VARCHAR(200) NOT NULL,
    comment TEXT NOT NULL,
    semester_taken VARCHAR(20),
    professor VARCHAR(100),
    grade_received VARCHAR(10),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_flagged BOOLEAN DEFAULT FALSE,
    is_approved BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (user_id) REFERENCES user(id)
);
```

## File Structure

```
app/
├── models.py              # Database models for User and Review
├── forms.py               # WTForms for authentication and reviews
├── routes.py              # Flask routes for auth and reviews
├── __init__.py            # App factory with database setup
├── templates/
│   ├── auth/
│   │   ├── login.html     # User login form
│   │   └── register.html  # User registration form
│   ├── reviews/
│   │   ├── add_review.html   # Review submission form
│   │   └── edit_review.html  # Review editing form
│   ├── base.html          # Updated with auth navigation
│   └── course_detail.html # Updated with reviews section
└── static/
    ├── css/style.css      # Updated with auth and review styling
    └── js/app.js          # Updated with flash message handling
```

## API Routes

### Authentication Routes

- `GET/POST /login` - User login
- `GET/POST /register` - User registration
- `GET /logout` - User logout (requires login)

### Review Routes

- `GET/POST /course/<course_code>/review` - Add new review (requires login)
- `GET/POST /course/<course_code>/review/edit` - Edit existing review (requires login)
- `POST /course/<course_code>/review/delete` - Delete review (requires login)

### Enhanced Course Routes

- `GET /course/<course_code>` - Course detail page with reviews and statistics

## Usage Examples

### User Registration

1. Navigate to `/register`
2. Enter full name and @illinois.edu email
3. Create secure password (minimum 6 characters)
4. Account created and automatically logged in

### Submitting a Review

1. Navigate to any course detail page
2. Click "Leave a Review" button (login required)
3. Fill out comprehensive review form:
   - Title and detailed comment
   - Overall rating, difficulty, and workload
   - Optional: semester, professor, grade
4. Submit review for immediate display

### Review Display

Reviews are shown on course pages with:

- Star ratings and numeric scores
- Author name and submission date
- Full review title and comment
- Optional context (semester, professor, grade)
- Average statistics in sidebar

## Form Validation

### Client-Side Validation

- Email format and @illinois.edu requirement
- Password confirmation matching
- Required field validation
- Character limits and minimums

### Server-Side Validation

- Duplicate email prevention
- Comment length validation (50-2000 characters)
- Rating range validation (1-5)
- Basic content filtering
- One review per course per user

## Security Features

### Authentication Security

- Password hashing with Werkzeug
- Session management with Flask-Login
- CSRF protection with Flask-WTF
- Login required decorators
- Secure cookie configuration

### Content Moderation

- Basic inappropriate content filtering
- Review approval system (default: approved)
- Flagging system for problematic content
- User-specific review management

## Installation & Setup

### Dependencies

```bash
pip install -r requirements.txt
```

Required packages:

- Flask==2.3.3
- Flask-Login==0.6.3
- Flask-SQLAlchemy==3.0.5
- Flask-WTF==1.2.1
- WTForms==3.1.0
- Werkzeug==2.3.7
- email-validator==2.1.0

### Database Setup

```python
from app import create_app
from app.models import db

app = create_app()
with app.app_context():
    db.create_all()  # Creates tables automatically
```

### Environment Variables

```bash
export SECRET_KEY="your-secret-key-here"
export DATABASE_URL="sqlite:///course_compass.db"  # Optional
```

### Running the Application

```bash
python run.py
```

## Testing

### Automated Testing

```bash
python test_review_system.py
```

Tests cover:

- User email validation
- Review display formatting
- Course statistics calculation
- Form validation logic
- Database schema simulation

### Manual Testing

1. Register with @illinois.edu email
2. Submit review for any course
3. Edit and delete reviews
4. View course statistics
5. Test login/logout functionality

## Features in Action

### Course Statistics

- **Average Ratings**: Calculated from all approved reviews
- **Difficulty Assessment**: Help students understand course challenge
- **Workload Expectations**: Plan semester schedule effectively
- **Review Count**: See how many students have shared experiences

### Review Quality

- **Minimum Standards**: 50-character minimum, 10-word minimum
- **Structured Feedback**: Separate ratings for different aspects
- **Contextual Information**: Semester and professor context
- **Authentic Reviews**: Illinois email requirement ensures student authenticity

### User Experience

- **Seamless Integration**: Reviews appear naturally in course flow
- **Mobile Responsive**: Works on all devices
- **Fast Loading**: Efficient database queries and caching
- **Clear Navigation**: Breadcrumbs and intuitive flow

## Future Enhancements

### Content Features

- Review helpfulness voting
- Professor-specific review filtering
- Photo uploads for assignments/projects
- Anonymous review options

### Moderation Features

- Advanced content filtering
- Community reporting system
- Moderator dashboard
- Review verification system

### Analytics Features

- Course popularity tracking
- Review sentiment analysis
- Department comparison metrics
- Trending courses identification

This review system transforms the Course Compass into a comprehensive platform where students can make informed decisions based on peer experiences, similar to Rate My Professor but tailored specifically for UIUC course planning.
