__author__ = 'PGY'

import sys
import os.path
import datetime
import requests
import threading

class TransCrawler:
    '''Web Crawler to get the translated word from google translation'''
    def __init__(self, inlang, outlang, theword):
        self.user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
        self.headers = {'User-Agent' : self.user_agent}
        self.inlang = inlang
        self.outlang = outlang
        self.theword = theword
        self.keywords ={'sl': self.inlang, 'tl': self.outlang, 'ie':'UTF-8', 'q': self.theword}
        self.url = 'http://translate.google.com/m'

    def getPage(self):
        url = self.url
        keywords = self.keywords
        try:
            response = requests.get(url, keywords, headers = self.headers)
            content = response.text
            return content
        except requests.exceptions.RequestException as e:
            print(e)
            return None

    def getWord(self):
        mark='class="t0">'
        content = self.getPage()
        if not content:
            print('Load page failed!')
            return None
        else:
            #return content
            startpos = content.index(mark)
            remaincont = content[content.find(mark)+len(mark):]
            result = remaincont.split('<')[0]
            return result

def transword_writeoutput(inword, outfilename):
    '''read a word string and save the input word and the output translation into a csv file'''
    inlang = 'de'
    outlang = ['en', 'zh']
    output_list = [inword]
    for lan in outlang:
        newword = TransCrawler(inlang, lan, inword)
        output_list.append(newword.getWord())
    outstr = ",".join(output_list) + "\n"
    with open(outfilename, 'a', encoding='utf-8') as text_file:
        text_file.write(outstr)

# get the input word list
inputfile = sys.argv[1]
datemark = datetime.datetime.now().strftime('%m.%Y')
with open(inputfile, 'r', encoding = 'utf-8') as f:
    first_line = f.readline()
inwordlist = first_line.split(datemark)[1].split()
unique_inwordlist = list(set(inwordlist))

# define output file name
outfilename = os.path.splitext(inputfile)[0] + '_GoAnki.csv'

# if the output already exists in current direcotry, remove it. Otherwise do nothing.
try:
    os.remove(outfilename)
except OSError:
    pass

# translate the words in word list and save the results in a csv file with multithread (speed up)
jobs = []
for word in unique_inwordlist:
    thread = threading.Thread(target=transword_writeoutput, args = (word,), kwargs = {'outfilename' : outfilename})
    jobs.append(thread)

for j in jobs:
    j.start()

for j in jobs:
    j.join()

