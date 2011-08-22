import os

r = os.statvfs(path)
freespace = r.f_bsize * r.f_bavail / 1024 / 1024