from app import create_app
import os

# Load environment variables from .env file

app = create_app()

if __name__ == '__main__':
    debug_mode = False
    app.run(debug=debug_mode)