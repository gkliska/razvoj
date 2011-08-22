#!/usr/bin/python
import os
from subprocess import Popen, PIPE, STDOUT

log = ''
if __name__ == '__main__':
    import string
    task_name = 'elso'
    task_name = task_name.replace(' ', '_')
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    task_name = ''.join(c for c in task_name if c in valid_chars)

    target_path = '/mnt/71a59876-8e5b-11df-81fa-001c259ff950'
        
    job_path = target_path + '/oerp_filestore'

    from_path = '/home/dukai/sysadmin_microcer'
try:
    if not job_path:
        job_path = os.path.join(target_path, task_name)
        os.mkdir(job_path)
    cmd = 'rsync -av ' + from_path + ' ' + job_path
    p = Popen(cmd, stdout=PIPE, stderr=STDOUT, shell=True)
    log += str(p.communicate()[0])
    success = True
except Exception, e:
    log += str(e)
    if __name__ == '__main__':
        print log
    success = False