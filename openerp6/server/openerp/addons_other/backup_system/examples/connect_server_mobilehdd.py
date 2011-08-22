#!/usr/bin/python
import uuid
import StringIO
import pexpect
from subprocess import Popen, PIPE
log = ''
path = None
if __name__ == '__main__':
    params = {
        'password': 'mypass',
    }
try:
    pipe = Popen('dmesg', stdout=PIPE, shell=True)
    dmesg = pipe.stdout.read()
    i = dmesg.index('WD       1600BEA')
    i = dmesg.index('[sd', i)
    devname = 'sd' + dmesg[i + 3] + '1'
    path = '/mnt/' + str(uuid.uuid1())
    child = pexpect.spawn('sudo mkdir -m 777 ' + path)
    s = StringIO.StringIO()
    child.logfile = s
    child.expect(['ssword', pexpect.EOF])
    child.sendline(params['password'])
    r = child.expect(['Sorry, try again.', pexpect.EOF])
    if r == 0:
        path = None
        raise Exception(s.getvalue())
    child.close()
    child = pexpect.spawn('sudo mount /dev/' + devname + ' ' + path)
    child.logfile = s
    r = child.expect(['ssword', 'mount: ', pexpect.EOF])
    if r == 1:
        raise Exception(s.getvalue())
    child.sendline(params['password'])
    r = child.expect(['ssword', 'mount: ', pexpect.EOF])
    if r == 1:
        raise Exception(s.getvalue())
    child.close()
    success = True
except Exception, e:
    log += str(e)
    if __name__ == '__main__':
        print log
    success = False
finally:
    if path:
        child = pexpect.spawn('sudo rmdir ' + path)
        child.expect(['ssword', pexpect.EOF])
        child.sendline(params['password'])
        child.expect(pexpect.EOF)
        child.close()