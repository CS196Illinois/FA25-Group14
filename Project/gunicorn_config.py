# Gunicorn configuration file for Render deployment

import os

# Server socket
bind = f"0.0.0.0:{os.environ.get('PORT', '10000')}"
backlog = 2048

# Worker processes
workers = 4
worker_class = 'sync'
worker_connections = 1000
timeout = 120
keepalive = 5

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = 'course_compass'

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL (handled by Render)
# These are managed by Render's infrastructure

# Server hooks
def on_starting(server):
    print("Starting Course Compass application...")

def on_reload(server):
    print("Reloading Course Compass application...")

def when_ready(server):
    print("Course Compass is ready to accept connections")

def on_exit(server):
    print("Shutting down Course Compass application...")
