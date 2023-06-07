from multiprocessing import cpu_count

# Socket Path
bind = 'unix:/home/viktor-shved/lavkach/gunicorn.sock'

# Worker Options
workers = cpu_count() + 1
worker_class = 'uvicorn.workers.UvicornWorker'

# Logging Options
loglevel = 'debug'
accesslog = '/home/viktor-shved/lavkach/access_log'
errorlog = '/home/viktor-shved/lavkach/error_log'
