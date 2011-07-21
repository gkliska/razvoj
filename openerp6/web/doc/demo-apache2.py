#!/usr/bin/python

import glob
import optparse
import os
import signal
import subprocess
import time

base = os.path.dirname(os.path.abspath(__file__))


def start():
    # workaround for https://bugs.launchpad.net/openobject-client-web/+bug/711190
    for session in glob.glob(os.path.join('/tmp', 'session-*')):
        os.remove(session)

    subprocess.call(['apache2', '-f',  os.path.join(base, 'apache2.conf'), '-d', base,
        '-c', 'WSGIPythonPath %s' % base,
        '-c', 'WSGIScriptAlias / %s/wsgi_app.py' % base])

def stop():
    try:
        pid = int(open(os.path.join(base, 'apache2.pid')).read())
    except:
        pass
    else:
        os.kill(pid, signal.SIGTERM)

def main():
    parser = optparse.OptionParser('%prog start|stop|restart')
    options, args = parser.parse_args()
    if len(args) != 1:
        parser.error('Incorrect argument')
    if args[0] == 'start':
        start()
    elif args[0] == 'stop':
        stop()
    elif args[0] == 'restart':
        stop()
        time.sleep(2)
        start()

if __name__ == '__main__':
    main()

