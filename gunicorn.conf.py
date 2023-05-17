import logging


bind = "0.0.0.0:8000"
worker_connections = 1000
workers = 4
threads = 2
timeout = 300
accesslog = '-' 
loglevel = str(logging.INFO)