#!/usr/bin/python
import socket
import time
import os, os.path
import signal
import re
from daemon import runner, DaemonContext
import logging
import syslog
import json

SOCKET='/tmp/sock'
K=10
K2=5
T=3
STDLOG='/dev/tty'
STDERR='/dev/tty'
DUMPFILE_K='/tmp/topk.json'
PIDFILE='/tmp/kirka.pid'
RUNNING = True
MAX_DATAGRAM_SIZE = 4096

class SpaceSaving():
    def __init__(self):
        self.counters   = {}
        self.candidates = {}
    def add(self, item, k, k2, t):
        if item in self.counters:
            self.counters[item] = self.counters[item] + 1
        elif len(self.counters) < k:
            self.counters[item] = 1
        else:
            if item in self.candidates:
                self.candidates[item] = self.candidates[item] + 1
                if self.candidates[item] == t:
                    dropout = min(self.counters, key=self.counters.get)
                    del self.counters[dropout]
                    self.counters[item] = t
                    del self.candidates[item]
                    return dropout
            elif len(self.candidates) < k2:
                self.candidates[item] = 1
            else:
                del self.candidates[min(self.candidates, key=self.candidates.get)]
                self.candidates[item] = 1
    def returnItems(self):
        return self.counters
    def returnCandidates(self):
        return self.candidates

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
                item = self.topk.add(datagram, K, K2, T)
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
        if not os.path.exists(DUMPFILE_K):
            with open(DUMPFILE_K, 'w') as fp:
                json.dump(self.topk.returnItems(), fp)

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
