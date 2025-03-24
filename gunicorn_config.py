bind = "0.0.0.0:10000"
workers = 4
worker_class = "gevent"
wsgi_app = "assessment.wsgi:application"  # Correct format: module:variable
timeout = 120 