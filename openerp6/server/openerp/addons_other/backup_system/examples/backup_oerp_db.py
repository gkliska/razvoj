#!/usr/bin/python
import shutil
import os

log = ''
if __name__ == '__main__':
    import string
    task_name = 'elso'
    task_name = task_name.replace(' ', '_')
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    task_name = ''.join(c for c in task_name if c in valid_chars)

    target_path = '/mnt/b75a6f02-89bc-11df-9691-001c259ff950'
        
    from _utils import make_archive
    import datetime
    date = datetime.datetime.today()

    from_path = '/var/backups/sl'
try:
    to_filename = task_name + '_' + date.strftime('%Y-%m-%d_%H-%M-%S')
    to_path = os.path.join(target_path, to_filename)
    job_path = make_archive(to_path, 'tar', from_path)
    success = True
except Exception, e:
    log += str(e)
    if __name__ == '__main__':
        print log
    success = False