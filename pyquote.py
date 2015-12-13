from __future__ import division
from splinter import Browser
from urlparse import urlparse, parse_qs, urljoin
from bs4 import BeautifulSoup as bs
import requests
import re
import os
import sys
from unidecode import unidecode
from PIL import ImageFont, Image, ImageDraw, ImageOps
from image_utils import ImageText
import traceback



class Google:
    def __init__(self):        
        self.browser=Browser()
        self.url = "http://images.google.com/"

    def __enter__(self):
        return self

    def search(self,keyword):
        self.browser.visit(self.url)
        self.browser.fill('q', keyword)
        button = self.browser.find_by_name('btnG')
        button.click()
        p=self.browser.find_by_css('div.rg_el:nth-child(1) > a:nth-child(1)')
        # print p
        try:
            imgurl = parse_qs(urlparse(p['href']).query)['imgurl'][0]
            print imgurl
            return imgurl
        except Exception as e:
            print e,'error here'
            return None

    def teardown(self):
        self.browser.quit()

    def __exit__(self, exc_type, exc_value, traceback):
        self.teardown()



def fetchquotes(keyword):
    nextlink=True
    url='http://www.brainyquote.com/quotes/keywords/{}.html'.format(keyword)
    r=requests.get(url)
    if r.status_code == 200:
        while nextlink:
            soup=bs(r.content,'lxml')
            for auth,quote in ((div.find('div','bq-aut').text , '{}   -{}'.format(div.find('span','bqQuoteLink').text,div.find('div','bq-aut').text)) for div in soup.select('div.masonryitem')):
                yield auth,quote
            
            nextlink=soup.find('a',href=True,text='Next')
            if nextlink:
                nextpage=urljoin(url,nextlink.get('href'))
                r=requests.get(nextpage)
    else:
        print 'Keyword {} not found'.format(keyword)



def download_image(name,url,directory):
    try:
        ext=url.rsplit('.')[-1][:3]
    except:
        ext='png'
    c=1
    fname='{}/{}.{}'.format(directory,name,ext)
    while os.path.exists(fname):
        c+=1
        fname='{}/{}.{}'.format(directory,name+str(c),ext)
        # name+=str(c)
        print 'Downloading Image'
    r=requests.get(url)
    with open(fname,'w') as f:
        f.write(r.content)
    print 'Done Downloading'
    return fname



def add_quote(infile,text):
    text=unidecode(text)
    maxwidth,maxheight = 640.0,480.0
    page = Image.open(infile)
    page=page.convert('RGB')
    ratio = min(maxwidth/page.size[0], maxheight/page.size[1])
    page.thumbnail((int(page.size[0]*ratio),int(page.size[1]*ratio)), Image.ANTIALIAS)
    w,h=page.size
#     print w,h
    rs = []
    gs = []
    bs = []
    for y in range(10):
        for x in range(page.size[0]):
#             print page.getpixel((x, page.size[1]-1-y))
            r, g, b = page.getpixel((x, page.size[1]-1-y))
            rs.append(r)
            bs.append(g)
            gs.append(g)
    bkcolor = tuple(map(lambda l:sum(l)/len(l),[rs,gs,bs]))
    r,g,b=bkcolor

    magic_no = ((r*299)+(g*587)+(b*114))/1000
    fgcolor= (0,0,0) if magic_no >=128 else (255,255,255)
    bkcolor = tuple(map(int, bkcolor))
    # if sum(bkcolor) >30:
    #     magic_number=max(bkcolor)+min(bkcolor)
    #     fgcolor = tuple(map(lambda x:magic_number-x,bkcolor))   
    # else:
    #     fgcolor=255,255,255


    temp=ImageText((w, 1000), background=bkcolor)

    width,height=temp.write_text_box((5,0), text, box_width=w, font_filename='Times_New_Roman.ttf',font_size=25, color=fgcolor)
    textbox=temp.image.crop( (0,0,width,height+50) )
    output=Image.new("RGB", (width,h+height+50),bkcolor)
    output.paste(page,(0,0))
    output.paste(textbox,(0,h))
    output.save(infile)
    page.close()
    output.close()


def main():
    if len(sys.argv) <1:
        print 'needs keyword as argument'
        sys.exit(0)

    keyword=sys.argv[1]
    directory='output/{}'.format(keyword)
    if not os.path.exists(directory):
        os.makedirs(directory)
    with Google() as google:
        for qno,(author,quote) in enumerate(fetchquotes(keyword),start=1):
            print 'Fetched quote no.{} by {}'.format(qno,author) 
            try:
                img=google.search(author)
                if not img:
                    continue

                fname = download_image(author, img, directory)
                add_quote(fname, quote)
                print fname,'written\n****************************\n\n'
            except Exception as e:
                traceback.print_exc()
                continue
        


if __name__ == '__main__':
    main()

