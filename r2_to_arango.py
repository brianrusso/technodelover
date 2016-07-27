from technodeminer.r2.model import R2, r2file_to_arango
from technodeminer.r2.util import get_filenames
from redis import Redis
from rq import Queue

r2_files = get_filenames('/media/sf_Data/CTV_R2')

if __name__ == '__main__':
    q= Queue(connection=Redis())
    for file in r2_files:
        q.enqueue(r2file_to_arango, file)
        print "Loading %s" % (file)
