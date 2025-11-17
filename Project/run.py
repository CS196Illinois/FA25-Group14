from app import create_app
import os

app = create_app()

if __name__ == '__main__':
    # For local development only
    # In production, gunicorn will import the 'app' object directly
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=debug_mode, use_reloader=False)