from __future__ import division
import gevent
from gevent import monkey
from gevent.pool import Pool
monkey.patch_all()
from os.path import splitext,join,exists
import os
import sys
import traceback
import argparse
from quotemine import *
from imagesearch import *
from makememe import *
from datetime import datetime
from random import randint




def download_image(name,url,directory):
    r=requests.get(url)
    try:
        ext=splitext(urlsplit(url).path)[-1]
    except:
        ext='.png'
    c=1
    fname=join(directory,name+ext)
    while os.path.exists(fname):
        c+=1
        fname=join(directory,name+str(c)+ext)
    with open(fname,'w') as f:
        f.write(r.content)
    return fname

def worker(args):
    with gevent.Timeout(60, False):
        name,url,directory,text, qno = args
        fname=download_image(name,url,directory)
        rv=make_meme(fname, text, url)
        print 'Quote no {} by {} done'.format(qno,name)
        if rv:
            return url,fname
        else:
            return url,'Error'

def fetch_results(args):
    headless = not args.firefox
    keyword = args.keyword
    quoteminer=QuoteMiner(source=args.source)
    
    directory='output/{}_{}'.format(keyword,args.source)
    if not os.path.exists(directory):
        os.makedirs(directory)

    with Google(headless=headless) as google:
        for qno,(author,quote) in enumerate(quoteminer.fetchquotes(keyword),start=1):
            # print 'Processing quote',qno,
            try:
                img=google.search(author)    
                yield author,img,directory,quote, qno
            except:
                traceback.print_exc()
                if args.total: args.total+=1
                continue
            if args.total and qno>=args.total:
                break



def main():
    parser=argparse.ArgumentParser(description="Generates quotation memes from keywords",)
    parser.add_argument('keyword',help='the keyword to search quotes with')
    parser.add_argument('-t','--total',help='''total images.''',type=int)
    parser.add_argument('-s','--source',help='''bq for Brainyquote, gr for Goodreads(default)''',type=str,default='gr')
    parser.add_argument('-f','--firefox',help='''use firefox, by default uses phantomjs''',action='store_true')
    args=parser.parse_args()
    pool = Pool(5)
    starttime=datetime.now()
    output=pool.map(worker, fetch_results(args))
    print 'REPORT: \n\n'
    for i,j in output:
        print i,j
    print 'All done in', datetime.now()-starttime




if __name__ == '__main__':
    main()

