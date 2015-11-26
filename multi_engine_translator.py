__author__ = 'PGY'

import sys
import os.path
import re
import requests
import threading
import urllib.parse
from bs4 import BeautifulSoup
from collections import deque

class fetch_page:
    user_agent = 'mozilla/4.0 (compatible; msie 5.5; windows nt)'
    headers = {'user-agent' : user_agent}

    @classmethod
    def getpage(cls, url, keywords):
        try:
            response = requests.get(url, keywords, headers = cls.headers)
            content = response.text
            return content
        except:
            e = sys.exc_info()
            print(e)
            return None

    @classmethod
    def getsoup(cls, content):
        if not content:
            print('Load page failed!')
            return None
        else:
            soup = BeautifulSoup(content, "lxml")
            return soup

class strformator:
    @staticmethod
    def keywordsdict(**kwargs):
        return kwargs

    @staticmethod
    def mergeurl(mainurl, path):
        return urllib.parse.urljoin(mainurl, path)

class google:
    def __init__(self, inlang, outlang, theword):
        self.inlang = inlang
        self.outlang = outlang
        self.theword = theword
        # --------------------------
        self.mainurl = 'http://translate.google.com/'
        self.path = 'm'
        self.keywords = strformator.keywordsdict(sl = self.inlang, tl = self.outlang, ie = 'UTF-8', q = self.theword)
        # -------------------------
        self.url = strformator.mergeurl(self.mainurl, self.path)
        self.page = fetch_page.getpage(self.url, self.keywords)

    def getanswer(self):
        mark='class="t0">'
        content = self.page
        if not content:
            print('Load page failed!')
            return None
        else:
            startpos = content.index(mark)
            remaincont = content[content.find(mark)+len(mark):]
            result = remaincont.split('<')[0]
            return result

    def format_inword(self):
        inwordfull = self.theword
        return inwordfull

class linguee:
    def __init__(self, inlang, outlang, theword):
        self.inlang = inlang
        self.outlang = outlang
        self.theword = theword
        # --------------------------
        self.mainurl = 'http://www.linguee.com/'
        self.path = '/'.join(('-'.join((inlang, outlang)), 'search'))
        self.keywords = strformator.keywordsdict(source = 'auto', query = self.theword)
        # -------------------------
        self.url = strformator.mergeurl(self.mainurl, self.path)
        self.page = fetch_page.getpage(self.url, self.keywords)
        self.soup = fetch_page.getsoup(self.page)
        self.genderdict = {
                'masculine' : 'der',
                'feminine'  : 'die',
                'neuter'    : 'das',
                'plural'    : 'die',
                'X'         : ''
                }

    def getinword_frompage(self):
        try:
            inword_tag = self.soup.find('span', class_ = 'dictTerm').string
        except AttributeError as e:
            inword_tag = self.theword
        return inword_tag

    def getanswer(self):
        answer_tag_list = self.soup.find_all('a', class_ = 'dictLink')
        if answer_tag_list and len(answer_tag_list) > 1:
            short_tag_list = answer_tag_list[:2]
            answerstr = '; '.join([tag.string for tag in short_tag_list])
        else:
            try:
                answerstr = answer_tag_list[0].string
            except IndexError:
                answerstr = None
        return answerstr

    def gettype(self):
        try:
            typestr = self.soup.find('span', class_ = 'tag_wordtype').string
        except AttributeError:
            typestr = None
        return typestr

    def format_inword(self):
        inword = self.getinword_frompage()
        typestr = self.gettype()
        if typestr and 'noun' in typestr:
            wordtype = typestr.split(',')[0].strip()
            noun_gender = typestr.split(',')[-1].strip()
            noun_gender_mark = self.genderdict.get(noun_gender, 'X')
            inwordfull = '{} {} ({})'.format(noun_gender_mark, inword, wordtype)
        elif typestr and ',' in typestr:
            wordtype = typestr.split(',')[0].strip()
            inwordfull = '{} ({})'.format(inword, wordtype)
        elif typestr:
            wordtype = typestr
            inwordfull = '{} ({})'.format(inword, wordtype)
        else:
            inwordfull = inword
        return inwordfull

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

# This function is useful only when multithread is switch off
# Because multithread will destroy the order later
# If set() is slower than O(n), this can be used for the speed purpose
# def del_dups(seq):
#     '''function to delete duplicate while preserve order'''
#     seen = {}
#     newlist = []
#     for item in seq:
#         if item not in seen:
#             seen[item] = True
#             newlist.append(item)
#     return newlist
def html_decode(s):
    """
    Returns the ASCII decoded version of the given HTML string. This does
    NOT remove normal HTML tags like <p>.
    """
    htmlCodes = (
            ("'", '&#39;'),
            ('"', '&quot;'),
            ('>', '&gt;'),
            ('<', '&lt;'),
            ('&', '&amp;')
        )
    for code in htmlCodes:
        s = s.replace(code[1], code[0])
    return s

def is_sentance(instr):
    if " " in instr.strip():
        return True
    else:
        return False

def transword_writeoutput(inword, inlang, outlang_list, outfilename):
    '''read a word string and save the input word and the output translation into a csv file'''
    output_list = []
    if 'en' in outlang_list and not is_sentance(inword):
        trans = linguee(inlang, 'en', inword)
        firstelement = trans.format_inword()
    else:
        firstelement = inword

    output_list.append(firstelement)

    for lan in outlang_list:
        if lan is 'en' and not is_sentance(inword):
            transnew = linguee(inlang, lan, inword)
            output_list.append(transnew.getanswer())
        else:
            transnew = google(inlang, lan, inword)
            output_list.append(transnew.getanswer())
    print(inword, output_list)
    outstr = ",".join(output_list) + ",\n"
    outstrparsed = html_decode(outstr)
    with open(outfilename, 'a', encoding='utf-8') as text_file:
        text_file.write(outstrparsed)

# get the input word list
inputfile = sys.argv[1]

dateregex = re.compile('\d{2}\.\d{2}\.\d{4}')
# if the file is saved from AutoNotes then it is a string
# read a string from a file
if '_AutoNotes' in inputfile:
    with open(inputfile, 'r', encoding = 'utf-8') as f:
        first_line = f.readline()
        fieldsepstr = dateregex.search(first_line).group()
        inwordlist = first_line.split(fieldsepstr)[1].split()

# if the file is self-created then it contains multi-lines with empty lines
# read the the lines and ignore the empty lines and the header (the line containing dateregex)
else:
    with open(inputfile, 'r', encoding = 'utf-8') as f:
        linesgen = (line.rstrip() for line in f)
        inwordlist = [line for line in linesgen if line and not dateregex.search(line)]

# Delete duplicate in the input list
# Preserve order is only useful when multithread is switch off
# Not sure about the BigO of set(a_list), if it is O(n*log(n))
# del_dups can be used to speed up
#unique_inwordlist = del_dups(inwordlist) # BigO -> O(n)

unique_inwordlist = list(set(inwordlist)) # BigO -> set(a_list): O(n*log(n)) or O(n)???

# define output file name
outfilename = os.path.splitext(inputfile)[0] + '_GoAnki.csv'

# if the output already exists in current direcotry, remove it. Otherwise do nothing.
try:
    os.remove(outfilename)
except OSError:
    pass

# translate the words in word list and save the results in a csv file with multithread (speed up)
jobs = []
inlang = 'de'
outlang = ['en', 'zh']
for word in unique_inwordlist:
    thread = threading.Thread(target=transword_writeoutput, args = (word,), kwargs = strformator.keywordsdict(inlang = inlang, outlang_list = outlang, outfilename = outfilename))
    jobs.append(thread)

for j in jobs:
    j.start()

for j in jobs:
    j.join()

