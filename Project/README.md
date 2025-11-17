# Course Compass 🧭

A comprehensive course review and planning platform for UIUC students. Get AI-powered recommendations, read peer reviews, track your gen-ed requirements, and connect with classmates.

## 🚀 Features

- **AI Course Recommendations**: Get personalized course suggestions using Google's Gemini AI
- **Course Reviews**: Read and write detailed reviews including ratings, difficulty, workload, and professor feedback
- **Gen-Ed Tracker**: Track your general education requirements progress
- **Course Chat**: Real-time messaging with other students in each course
- **Advanced Search**: Filter courses by department, level, gen-ed requirements, and more
- **GPA Calculator**: View average grades and GPA statistics for courses

## 🛠️ Tech Stack

- **Backend**: Flask (Python)
- **Database**: Supabase (PostgreSQL)
- **Frontend**: HTML, CSS, JavaScript
- **AI**: Google Gemini API
- **Deployment**: Render
- **Authentication**: Flask-Login

## 📋 Prerequisites

- Python 3.11+
- Supabase account
- Google Gemini API key (optional, for AI recommendations)

## 🏃 Quick Start

### Local Development

1. **Clone the repository**:
   ```bash
   git clone https://github.com/CS196Illinois/FA25-Group14.git
   cd Project
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   Create a `.env` file:
   ```env
   FLASK_ENV=development
   FLASK_DEBUG=True
   SECRET_KEY=your-secret-key-here
   
   # Supabase Configuration
   SUPABASE_URL=https://xxxxx.supabase.co
   SUPABASE_KEY=your-supabase-anon-key
   DATABASE_URL=postgresql://postgres:password@db.xxxxx.supabase.co:5432/postgres
   
   # Google Gemini (Optional)
   GOOGLE_API_KEY=your-google-api-key
   ```

5. **Set up Supabase database**:
   - Create a Supabase project at [supabase.com](https://supabase.com)
   - Run the SQL schema from `DEPLOYMENT.md` in Supabase SQL Editor
   - Or migrate existing SQLite data: `python migrate_sqlite_to_supabase.py`

6. **Run the application**:
   ```bash
   python run.py
   ```

7. **Open in browser**:
   Navigate to `http://localhost:5000`

## 🌐 Production Deployment (Render)

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

### Quick Deploy

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin master
   ```

2. **Deploy on Render**:
   - Go to [dashboard.render.com](https://dashboard.render.com)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Render will detect `render.yaml` automatically
   - Add environment variables in Render dashboard

3. **Configure Environment Variables** in Render:
   - `FLASK_ENV`: `production`
   - `FLASK_DEBUG`: `False`
   - `SECRET_KEY`: Generate a secure random string
   - `SUPABASE_URL`: Your Supabase project URL
   - `SUPABASE_KEY`: Your Supabase anon key
   - `DATABASE_URL`: Your Supabase connection string

4. **Deploy**: Click "Create Web Service"

Your app will be live at `https://your-app.onrender.com`

## 📁 Project Structure

```
Project/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── routes.py            # Route handlers
│   ├── models.py            # Database models
│   ├── forms.py             # WTForms
│   ├── supabase_functions.py  # Database operations
│   ├── static/              # CSS, JS, images
│   └── templates/           # HTML templates
├── experiments/             # Development/testing files
├── instance/                # Local SQLite database (dev only)
├── gunicorn_config.py       # Production WSGI config
├── render.yaml              # Render deployment config
├── requirements.txt         # Python dependencies
├── run.py                   # Application entry point
├── migrate_sqlite_to_supabase.py  # Data migration script
├── DEPLOYMENT.md            # Detailed deployment guide
└── README.md                # This file
```

## 🔧 Configuration

### Environment Variables

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `FLASK_ENV` | No | Environment (development/production) | `development` |
| `FLASK_DEBUG` | No | Enable debug mode | `False` |
| `SECRET_KEY` | Yes | Flask secret key for sessions | - |
| `SUPABASE_URL` | Yes | Supabase project URL | - |
| `SUPABASE_KEY` | Yes | Supabase anon/public key | - |
| `DATABASE_URL` | Yes | PostgreSQL connection string | SQLite (dev) |
| `GOOGLE_API_KEY` | No | Google Gemini API key | - |
| `PORT` | No | Port to run on | `5000` |

## 🧪 Testing

Run the test suite:

```bash
# Install pytest
pip install pytest

# Run all tests
pytest app/test_supabase_functions.py -v

# Run simple tests without pytest
python app/simple_test_supabase_functions.py
```

## 📊 Database Schema

The application uses four main tables:

- **user**: User accounts and authentication
- **review**: Course reviews with ratings and comments
- **message**: Course chat messages
- **user_requirements**: Gen-ed requirement tracking

See `DEPLOYMENT.md` for complete SQL schema.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit a pull request

## 📝 Development Notes

### Running Locally

- Use SQLite for local development (automatic)
- Set `FLASK_DEBUG=True` for auto-reload
- Access at `http://localhost:5000`

### Production Considerations

- Use Supabase PostgreSQL for production
- Set `FLASK_DEBUG=False` always
- Use strong `SECRET_KEY` (64+ characters)
- Enable HTTPS (automatic on Render)
- Monitor logs via Render dashboard

## 🐛 Troubleshooting

### Database Connection Issues

```bash
# Test Supabase connection
python -c "from app.supabase_functions import get_user_by_email; print(get_user_by_email('test@example.com'))"
```

### Migration Issues

```bash
# Migrate SQLite to Supabase
python migrate_sqlite_to_supabase.py
```

### Render Deployment Issues

- Check environment variables are set correctly
- View logs in Render dashboard
- Ensure `DATABASE_URL` format is correct
- Verify Supabase tables are created

## 📚 API Endpoints

### Public Endpoints
- `GET /` - Home page
- `GET /health` - Health check (monitoring)
- `GET /course/<code>` - Course detail page
- `POST /search` - Search courses

### Authenticated Endpoints
- `POST /login` - User login
- `POST /register` - User registration
- `POST /logout` - User logout
- `POST /course/<code>/review` - Submit review
- `GET /messages/<code>` - Get course messages
- `POST /messages/<code>` - Send message

## 🔒 Security

- Passwords hashed with Werkzeug
- CSRF protection on all forms
- Secure session cookies in production
- HTTPS enforced (via Render)
- SQL injection protection (SQLAlchemy ORM)

## 📄 License

This project is part of the CS196 course at UIUC.

## 👥 Team

CS196 Fall 2025 - Group 14

## 🙏 Acknowledgments

- UIUC course data
- Supabase for database hosting
- Render for application hosting
- Google Gemini for AI recommendations

## 📞 Support

For issues or questions:
1. Check [DEPLOYMENT.md](DEPLOYMENT.md) for deployment help
2. Review [GitHub Issues](https://github.com/CS196Illinois/FA25-Group14/issues)
3. Contact the development team

---

**Happy Course Planning! 🎓**
