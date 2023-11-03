from multiprocessing import cpu_count

# Socket Path
#bind = 'unix:/fundamental/viktor-shved/lavkach/gunicorn.sock'
bind = "127.0.0.1:8000"

# Worker Options
workers = cpu_count() + 1
worker_class = 'uvicorn.workers.UvicornWorker'

# Logging Options
loglevel = 'debug'
#accesslog = '/fundamental/viktor-shved/lavkach/access_log'
#errorlog = '/fundamental/viktor-shved/lavkach/error_log'
