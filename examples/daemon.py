#!/usr/bin/env python

import time
import os
import signal
import lockfile
import json
import logging as log
import logging.config

from conf import *
from daemon import runner, DaemonContext

# is SIGINT caught
RUNNING = True

def SIGINT_handler(signum, frame):
    global RUNNING

    log.info('SIGINT received, shutting down')
    RUNNING = False


class DroneDaemon():
    def __init__(self):
        """
        Temporarely set stdin, out and err to /dev/null, we'll override it later
        """
        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/null'
        self.stderr_path = '/dev/null'
        self.pidfile_path = DRONE_PID
        self.pidfile_timeout = 5

    def run(self):
        log.info('starting controller, send SIGINT to exit')
        global RUNNING

        signal.signal(signal.SIGINT, SIGINT_handler)

        while(RUNNING):
            log.info('running...')
            time.sleep(SLEEP_TIME)

        log.info('cleanup')
        log.info('done')

class DroneDaemonRunner(runner.DaemonRunner):
    def _terminate_daemon_process(self):
        """
        Terminate the daemon process gracefully, which is specified in the current PID file
        """
        pid = self.pidfile.read_pid()

        try:
            os.kill(pid, signal.SIGINT)
        except OSError, exc:
            raise DaemonRunnerStopFailureError(u'Failed to stop %(pid)d: %(exc)s' % vars())

if __name__ == '__main__':
    logging.config.dictConfig(LOG_CONFIG)
    log_file = log.root.handlers[0].stream

    # Create deamon runner and override the stdout, stderr to logfile
    drunner = DroneDaemonRunner(DroneDaemon())
    drunner.daemon_context.files_preserve = [log_file]
    # drunner.daemon_context.working_directory = os.getcwd()
    drunner.daemon_context.working_directory = os.path.dirname(os.path.abspath(__file__))
    drunner.daemon_context.stdout = log_file
    drunner.daemon_context.stderr = log_file
    drunner.daemon_context.signal_map = {
        signal.SIGINT: SIGINT_handler,
    }
    try:
        drunner.do_action()
    except lockfile.LockTimeout as e:
        log.warning('failed to ackquire the lock')
    except runner.DaemonRunnerStopFailureError as e:
        log.warning('failed to stop daemon: %s', e)

