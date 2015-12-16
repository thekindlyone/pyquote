from urlparse import urlparse, parse_qs, urljoin
from bs4 import BeautifulSoup as bs
import requests
import re
from unidecode import unidecode



class QuoteMiner(object):
    def __init__(self,source='gr',max_words=80):
        self.source=source
        gr_request=lambda keyword:requests.get('http://www.goodreads.com/quotes/search',params=dict(q=keyword,commit='Search'))
        bq_request=lambda keyword:requests.get('http://www.brainyquote.com/quotes/keywords/{}.html'.format(keyword))
        
        gr_quotes=lambda soup: ((div.find('a').text, div.text.strip().replace('\n',''))for div in soup.select('div.quoteText'))
        bq_quotes=lambda soup: ((div.find('div','bq-aut').text , '{}   -{}'.format(div.find('span','bqQuoteLink').text,div.find('div','bq-aut').text)) for div in soup.select('div.masonryitem'))
        
        bq_nextpage=lambda soup: soup.find('a',href=True,text='Next')
        gr_nextpage=lambda soup: soup.find('a','next_page')
        
        self.extractors=dict(
            gr={'request':gr_request,
                       'quotes':gr_quotes,
                       'nextpage':gr_nextpage},
            bq={'request':bq_request,
                         'quotes':bq_quotes,
                         'nextpage':bq_nextpage}
        )
        
    def fetchquotes(self,keyword):
        nextlink=True
        r = self.extractors[self.source]['request'](keyword)
        url = r.url
        quotes=self.extractors[self.source]['quotes']
        nextpage = self.extractors[self.source]['nextpage']
        if r.status_code == 200:
            while nextlink:
                soup=bs(r.content,'lxml')
                [s.extract() for s in soup('script')]
                for auth,quote in quotes(soup):
                    if len(quote.split())<80:
                        yield auth,unidecode(quote)

                nextlink=nextpage(soup)
                if nextlink:
                    nexturl=urljoin(url,nextlink.get('href'))
                    r=requests.get(nexturl)
        else:
            print 'Keyword {} not found'.format(keyword)