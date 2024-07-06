from multiprocessing import cpu_count
from os import environ


bind = environ.get('SOCKET_OVERRIDE', '0.0.0.0:' + environ.get('PORT', '5000'))
max_requests = 1000
worker_class = "uvicorn.workers.UvicornWorker"
workers = cpu_count()
timeout = 600
logconfig = 'logging.conf'
