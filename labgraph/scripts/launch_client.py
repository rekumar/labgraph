"""
The script to launch task_view and executor, which are the core of the system.
"""

import multiprocessing
import sys
import time
from threading import Thread

from gevent.pywsgi import WSGIServer

try:
    multiprocessing.set_start_method("spawn")
except RuntimeError:
    pass


def launch_dashboard(host: str, port: int, debug: bool = False):
    from ..dashboard import create_app

    if debug:
        print("Debug mode is on, the dashboard will be served with CORS enabled!")
    app = create_app(cors=debug)  # if debug enabled, allow cross-origin requests to API
    if debug:
        server = WSGIServer((host, port), app)  # print server's log on the console
    else:
        server = WSGIServer((host, port), app, log=None, error_log=None)
    server.serve_forever()


def launch_client(host, port, debug):

    dashboard_thread = Thread(target=launch_dashboard, args=(host, port, debug))

    dashboard_thread.daemon = True

    dashboard_thread.start()

    while True:
        time.sleep(1)
        if not dashboard_thread.is_alive():
            sys.exit(1001)
