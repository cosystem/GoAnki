__author__ = 'PGY'

import codecs, sys
import requests
import datetime

class TransCrawler:
    def __init__(self, urlnkeyword):
        self.user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
        self.headers = {'User-Agent' : self.user_agent}
        self.urlnkeyword = urlnkeyword

    def getPage(self):
        try:
            response = requests.get(self.urlnkeyword[0], self.urlnkeyword[1], headers = self.headers)
            content = response.text
            return content
        except requests.exceptions.RequestException as e:
            print(e)
            return None

    def getPageItem(self):
        mark='class="t0">'
        content = self.getPage()
        if not content:
            print('Load page failed!')
            return None
        else:
            startpos = content.index(mark)
            remaincont = content[content.find(mark)+len(mark):]
            result = remaincont.split('<')[0]
            return result

    def start(self):
        result = self.getPageItem()
        print(result)

class LangURLInfo:
    def __init__(self, inlang, outlang):
        self.inlang = inlang
        self.outlang = outlang
        self.theword = ''

    def geturl(self):
        keywords ={'sl': self.inlang, 'tl': self.outlang, 'ie':'UTF-8', 'q': self.theword}
        url = 'http://translate.google.com/m'
        return (url, keywords)

datemark = datetime.datetime.now().strftime('%m.%Y')
with open(sys.argv[1], 'r', encoding = 'utf-8') as f:
    first_line = f.readline()

inwordlist = first_line.split(datemark)[1].split()
info=LangURLInfo('de','en')
for word in inwordlist:
    info.theword = word
    crawler = TransCrawler(info.geturl())
    crawler.start()
