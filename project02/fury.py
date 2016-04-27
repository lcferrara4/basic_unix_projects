#!/usr/bin/env python2.7

import sys
import string
import itertools
import os
import json
import work_queue

#Main Execution

JOURNAL = {}
ALPHABET = string.ascii_lowercase + string.digits

if __name__ == '__main__':
    queue = work_queue.WorkQueue(9200, name ='hulk-eobaditc',catalog=True)
    queue.specify_log('fury.log')


    for i in range(1,6):
        command = './hulk.py -l {}'.format(i)
        if command in JOURNAL:
            print >>sys.stderr,'Already did',command
        task = work_queue.Task(command)
        for source in ('hulk.py','hashes.txt'):
            task.specify_file(source, source, work_queue.WORK_QUEUE_INPUT)
        queue.submit(task)

    for i in range(1,2):
        for prefix in itertools.product(ALPHABET,repeat=i):
            command = './hulk.py -l 6 -p {}'.format(prefix)
            if command in JOURNAL:
                print >>sys.stderr,'Already did',command
            task = work_queue.Task(command)
            for source in ('hulk.py','hashes.txt'):
                task.specify_file(source, source, work_queue.WORK_QUEUE_INPUT)
            queue.submit(task)

    while not queue.empty():
        task = queue.wait()
        if task and task.return_status == 0:
            sys.stdout.write(task.output)
            sys.stdout.flush()
            JOURNAL[task.command]=task.output.split()
            with open('journal.json.new','w') as stream:
                json.dump(JOURNAL,stream)
            os.rename('journal.json.new','journal.json')


