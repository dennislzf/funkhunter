#!/usr/bin/env python

'''

A script to generate JSON of the CNAME of a list of websites

'''

import os
import sys
import json
import requests
import dns.resolver
from urlparse import urlparse
from threading import Thread
from Queue import Queue
from datetime import datetime
import glob
agents = {
    'mobile': 'Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_2_1 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8C148 Safari/6533.18.5',
    'desktop': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.143 Safari/537.36'
}
concurrent = 500
q = Queue(concurrent *2)
#FUNCTION concatnate all json files into one huge one
def concat_json():
    output_json ={}
    cname_list = []
        #open all files and concat to list
    for filename in os.listdir('output/'):
        with open('output/'+filename, 'r') as f:
            data = "".join(f.read().split())
            data.decode('string_escape')
        cname_list.append(data)
    output_json['cnames'] = cname_list
    #get date stuff
    date = datetime.now()
    year = str(date.year)
    month = str(date.month)
    day = str(date.day)
    new_file = "cnames/output-%s-%s-%s.json" % (year,month, day)
    with open(new_file, 'w') as outfile:
        json.dump(output_json, outfile)
    #remove all the simple files
    files = glob.glob('output/*')
    for f in files:
        os.remove(f)


#FUNCTION used to get all the cnames of input csv
def get_cnames():
    while True:
        # process each chunk
        chunk = q.get()
        root_url = chunk
        www_url = 'www.' + chunk
        mobile_url = 'mobile.' + chunk
        m_url = 'm.' + chunk
        urls = [root_url,www_url,mobile_url,m_url]
        #set lifetime and timeout of resolver so we don't wait for forever
        resolver = dns.resolver.Resolver()
        resolver.timeout = 3
        resolver.lifetime = 3
        return_json = {}
        return_json['cnames'] = []
        for url in urls:
            new_cname ={}
            new_cname['cnameRecord'] = url
            try:
                answers = resolver.query(url, 'CNAME')
                for rdata in answers:
                    name = str(rdata.target)
                    new_cname['cname'] = name
                    with open(os.path.join('output', '%s.json' % url), 'w') as out:
                        out.write(json.dumps(new_cname, sort_keys=True, indent=4, separators=(',', ': ')))
            except Exception,e:
                pass
        q.task_done()



def parse_it(list):
    # set up folders
    output_path = 'output'
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    cname_path = 'cnames'
    if not os.path.exists(cname_path):
        os.makedirs(cname_path)

    diff_path = 'diffs'
    if not os.path.exists(diff_path):
        os.makedirs(diff_path)

    # chunk the inputs to allow for cleanup after each chunk
    chunks = []
    chunk_size = 1000

    # request each url in the list
    with open(list, 'r') as infile:
        for line in infile:
            stripped = line.strip()

            if stripped == '':
                return
            chunks.append(stripped)
    #set up dat threads
    for i in range(concurrent):
        t = Thread(target=get_cnames)
        t.daemon = True
        t.start()
    try:
        for chunk in chunks:
            q.put(chunk)
    except KeyboardInterrupt:
        sys.exit(1)
    #wait for all threads to finish
    print "GATHERING CNAMES"
    q.join()
    print "DONE GATHERING CNAMES"
    concat_json()


if __name__ == "__main__":

    if len(sys.argv) == 2:
        parse_it(sys.argv[1])
    else:
        print 'Usage: cname.py <plaintext file w/ URL on each line>'
