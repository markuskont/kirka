#!/usr/bin/env python
# coding: utf-8

import socket
import time
import os, os.path
import signal
import re
from daemon import runner, DaemonContext
import logging
import syslog
import json

from algorithms.SpaceSaving import *
from algorithms.Frequent import *

SOCKET='/tmp/sock'
K=10
K2=5
T=3
STDLOG='/dev/tty'
STDERR='/dev/tty'
DUMPFILE_K='/tmp/topk.dmp'
PIDFILE='/tmp/kirka.pid'
RUNNING = True
MAX_DATAGRAM_SIZE = 4096

class App():
    def __init__(self):
        self.stdin_path         = '/dev/null'
        self.stdout_path        = STDLOG
        self.stderr_path        = STDERR
        self.pidfile_path       = PIDFILE
        self.pidfile_timeout    = 5
        self.topk               = SpaceSaving()

    def run(self):
        syslog.syslog('starting daemon, send SIGINT to exit')
        global RUNNING

        signal.signal(signal.SIGINT, self.SIGINT_handler)
        signal.signal(signal.SIGHUP, self.SIGHUP_handler)

        if os.path.exists( SOCKET ):
            os.remove( SOCKET )
        syslog.syslog("Opening socket...")
        server = socket.socket( socket.AF_UNIX, socket.SOCK_DGRAM )
        server.bind(SOCKET)

        while(RUNNING):
            try:
                datagram = server.recv( MAX_DATAGRAM_SIZE )
                words = datagram.split()
                for word in words:
                    item = self.topk.add(word, K, K2, T)
                    if item:
                        print item
            except socket.timeout:
                continue
            except Exception as e:
                syslog.syslog(syslog.LOG_ERR, str(e))
                continue

        syslog.syslog("Shutting down...")
        server.close()
        os.remove( SOCKET )
        syslog.syslog("Done")

    def SIGINT_handler(self, signum, frame):
        global RUNNING
        syslog.syslog('SIGINT received, shutting down')
        RUNNING = False

    def SIGHUP_handler(self, signum, frame):
        syslog.syslog('SIGHUP received, dumping data')
        self.dumpCouners(self.topk.returnItems(), DUMPFILE_K)

    def dumpCouners(self, counters, dumpfile):
        if not os.path.exists(dumpfile):
            with open(dumpfile, 'w') as dump:
                json.dump(counters, dump)

class KDaemonRunner(runner.DaemonRunner):
    def _terminate_daemon_process(self):
        """
        Terminate the daemon process gracefully, which is specified in the current PID file
        """
        pid = self.pidfile.read_pid()

        try:
            os.kill(pid, signal.SIGINT)
        except OSError, exc:
            raise DaemonRunnerStopFailureError(u'Failed to stop %(pid)d: %(exc)s' % vars())

def main():
    kirka = KDaemonRunner(App())
    kirka.do_action()

if __name__ == "__main__":
    main()
