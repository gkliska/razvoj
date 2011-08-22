#!/usr/bin/python

import errno
from subprocess import Popen, PIPE, STDOUT

log = ''
if __name__ == '__main__':
    params = {
        'password': 'mypass',
    }
    path = '/mnt/c70f45ce-8a72-11df-9175-001c259ff950'
try:
    cmd = 'sudo -S umount ' + path
    p = Popen(cmd, stdout=PIPE, stdin=PIPE, stderr=STDOUT, shell=True)
    try:
        r = p.communicate(input=params['password'] + '\n')
    except OSError, e:
        #sudo didn't ask for password
        if e.errno == errno.EPIPE:
            r = p.communicate()
        else:
            raise
    if 'mount: ' in r[0]:
        raise Exception(r[0])
    cmd = 'sudo -S rmdir ' + path
    p = Popen(cmd, stdout=PIPE, stdin=PIPE, stderr=STDOUT, shell=True)
    success = True
except Exception, e:
    log += str(e)
    if __name__ == '__main__':
        print 'Failed'
        print log
    success = False