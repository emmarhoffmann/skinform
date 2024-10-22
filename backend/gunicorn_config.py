# Gunicorn configuration file
import os

# Number of worker processes
workers = int(os.getenv('WEB_CONCURRENCY', 3))

# Timeout for worker processes
timeout = 120

# Maximum requests a worker will process before restarting
max_requests = 1000
max_requests_jitter = 50

# Port to bind to
bind = f"0.0.0.0:{int(os.getenv('PORT', 10000))}"

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'

# Worker class
worker_class = 'sync'

# Prevent memory leaks
preload_app = True