#!/usr/bin/python
import socket
import time
import os, os.path
import signal
import re
from daemon import runner, DaemonContext
import logging
import syslog

SOCKET='/tmp/sock'
K=3
STDLOG='/var/log/kirka.log'
STDERR='/var/log/kirka.err'
RUNNING = True
MAX_DATAGRAM_SIZE = 4096

def SIGINT_handler(signum, frame):
    global RUNNING

    syslog.syslog('SIGINT received, shutting down')
    RUNNING = False

def SpaceSavingAdd(counters, item, k):
    if item in counters:
        counters[item] = counters[item] + 1
    elif len(counters) < k:
        counters[item] = 1
    else:
        item_with_least_hits = min(counters, key=counters.get)
        del counters[item_with_least_hits]
        counters[item] = 1
        #print "DROPPED: %s" % item_with_least_hits
    return counters

class App():
    def __init__(self):
        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/tty'
        self.stderr_path = '/dev/tty'
        self.pidfile_path =  '/tmp/kirka.pid'
        self.pidfile_timeout = 5

    def run(self):
        syslog.syslog('starting daemon, send SIGINT to exit')
        global RUNNING

        signal.signal(signal.SIGINT, SIGINT_handler)

        if os.path.exists( SOCKET ):
            os.remove( SOCKET )
        syslog.syslog("Opening socket...")
        server = socket.socket( socket.AF_UNIX, socket.SOCK_DGRAM )
        server.bind(SOCKET)
        counters = {}

        while(RUNNING):
            try:
                datagram = server.recv( MAX_DATAGRAM_SIZE )
                topk = SpaceSavingAdd(counters, datagram, K)
                print topk
            except socket.timeout:
                continue
            except:
                break

        syslog.syslog("Shutting down...")
        server.close()
        os.remove( SOCKET )
        syslog.syslog("Done")

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
