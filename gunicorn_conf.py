from multiprocessing import cpu_count

# Socket Path
bind = 'unix:/base/viktor-shved/lavkach/gunicorn.sock'

# Worker Options
workers = cpu_count() + 1
worker_class = 'uvicorn.workers.UvicornWorker'

# Logging Options
loglevel = 'info'
#accesslog = '/base/viktor-shved/lavkach/access_log'
#errorlog = '/base/viktor-shved/lavkach/error_log'
