from splinter import Browser
from selenium.common.exceptions import TimeoutException
from urlparse import urlparse, parse_qs, urljoin, urlsplit
from urllib import urlencode
class Google:
    def __init__(self,headless=True):
        if headless:        
            self.browser=Browser('phantomjs',
                    user_agent='Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
                    desired_capabilities={'loadImages': False})
        else:
            self.browser=Browser()
        self.browser.driver.set_page_load_timeout(45)
        self.url = 'http://www.google.co.in/search?{}'.format
        # (urlencode(dict(tbm='isch',q=keyword)))

    def __enter__(self):
        return self

    def search(self,keyword):
        try:
            self.browser.visit(self.url(urlencode(dict(tbm='isch',q=keyword))))
        except TimeoutException:
            return None
        # self.browser.fill('q', keyword)
        # button = self.browser.find_by_name('btnG')
        # button.click()
        p=self.browser.find_by_xpath('//div[@data-ri="0"]/a')[0]
        # p=self.browser.find_by_css('div.rg_el:nth-child(1) > a:nth-child(1)')
        # print p
        try:
            imgurl = parse_qs(urlparse(p['href']).query)['imgurl'][0]
            # print imgurl
            return imgurl
        except Exception as e:
            print e,'error here'
            return None

    def teardown(self):
        self.browser.quit()

    def __exit__(self, exc_type, exc_value, traceback):
        self.teardown()
