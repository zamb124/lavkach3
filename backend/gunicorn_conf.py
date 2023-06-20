from multiprocessing import cpu_count

# Socket Path
bind = 'unix:/fundamental/viktor-shved/lavkach/gunicorn.sock'

# Worker Options
workers = cpu_count() + 1
worker_class = 'uvicorn.workers.UvicornWorker'

# Logging Options
loglevel = 'info'
#accesslog = '/fundamental/viktor-shved/lavkach/access_log'
#errorlog = '/fundamental/viktor-shved/lavkach/error_log'
