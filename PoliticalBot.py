'''
Created on Feb 28, 2014

@author: nikola
'''
import urllib2
#beautiful soup needs to be installed using apt-get install python-bs4
from bs4 import BeautifulSoup
from urlparse import urlparse
import gc
import re
from HTMLParser import HTMLParser
import operator
from random import randint
from PIL import Image
import ImageEnhance
from pytesser import *
from urllib import urlretrieve
import urllib

def get(link):
    urlretrieve(link,'temp.png')

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()
stopwords = [line.strip() for line in open('stopwords')]
start_pages = ["http://www.b92.net/info/vesti/index.php?yyyy=2014&mm=02&dd=28&nav_category=11&nav_id=818066", "http://www.b92.net/biz/vesti/srbija.php?yyyy=2014&mm=02&dd=28&nav_id=818018", "http://www.b92.net/info/vesti/index.php?yyyy=2014&mm=02&dd=28&nav_category=11&nav_id=817915"]
for start_page in start_pages:
    f = urllib2.urlopen(start_page)
    parsed_uri = urlparse( start_page )
    domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
    print domain
    html = f.read()
    f.close()
    parsed_html = BeautifulSoup(html)
    comment_button = parsed_html.body.find('li', attrs={'class':'comment-send'})
    comment_link = domain[:-1] + comment_button.find('a')['href']
    article_text = parsed_html.body.find('div', attrs={'class':'article-text'})
    article_text = (re.subn(r'<(script).*?</\1>(?s)', '', str(article_text))[0])
    article_text = (re.subn(r'<(style).*?</\1>(?s)', '', str(article_text))[0])
    article_text = (re.subn(r'<(div) id="related-box".*?</\1>(?s)', '', str(article_text))[0])
    article_text = (re.subn(r'<(div) class="img-caption".*?</\1>(?s)', '', str(article_text))[0])
    article_text = (re.subn(r'<(div) id="social".*?</\1>(?s)', '', str(article_text))[0])
    article_text = (re.subn(r'Foto: Tanjug', '', str(article_text))[0])
    article_text = (re.subn(r'Tweet', '', str(article_text))[0])
    article_text = (re.subn(r'<(span) class="article-info2.*?</\1>(?s)', '', str(article_text))[0])
    article_text =  strip_tags(article_text)
    tokens = article_text.split(" ")
    tokens2 = {}
    for token in tokens:
        if(token not in stopwords):
            if(token not in tokens2):
                tokens2[token] = 1
            else:
                tokens2[token]= tokens2[token]+1
    sorted_tokens = sorted(tokens2.iteritems(), key=operator.itemgetter(1),reverse=True)          
    for x in range(0,10):
        print sorted_tokens[x]
        
    Leaders = [line.strip() for line in open('Leaders')]
    Parties = [line.strip() for line in open('Parties')]
    Unames = [line.strip() for line in open('UserNames')]
    LeaderComments = [line.strip() for line in open('LeaderComments')]
    PartyComments = [line.strip() for line in open('PartyComments')]
    leader = ''
    party = ''
    for x in range(0,10):
        if sorted_tokens[x][0] in Leaders:
            leader = sorted_tokens[x][0]
            break
    if leader == '':
        for x in range(0,10):
            if sorted_tokens[x][0] in Parties:
                party = sorted_tokens[x][0]
                break
    print "Leader = " + leader
    print "Party = " + party
    comment = ''
    if leader != '':
        comment = LeaderComments[randint(0,len(LeaderComments)-1)].replace('[Leader]', leader)
    else:
        comment = PartyComments[randint(0,len(PartyComments)-1)].replace('[Party]', party)
    print comment   
    f = urllib2.urlopen(comment_link)
    parsed_uri = urlparse( comment_link )
    html = f.read()
    f.close()
    parsed_html = BeautifulSoup(html)
    relative_image_link = parsed_html.body.find('img', attrs={'class':'captcha-attempt-image'})['src'][1:]
    capcha_image =domain+ relative_image_link
    print capcha_image
    # Source from: http://www.debasish.in/2012/01/bypass-captcha-using-python-and.html
    get(capcha_image);
    im = Image.open("temp.png")
    nx, ny = im.size
    im2 = im.resize((int(nx*5), int(ny*5)), Image.BICUBIC)
    im2.save("temp2.png")
    enh = ImageEnhance.Contrast(im)
    enh.enhance(1.7)#.show("30% more contrast")
    imgx = Image.open('temp2.png')
    imgx = imgx.convert("RGBA")
    pix = imgx.load()
    for y in xrange(imgx.size[1]):
        for x in xrange(imgx.size[0]):
            if pix[x, y][0]>120 and pix[x, y][1]>120 and pix[x, y][2]>120 and pix[x, y][3]>120:
                pix[x, y] = (255, 255, 255, 255)
            else:
                pix[x, y] = (0, 0, 0, 0)
    imgx.save("bw.gif", "GIF")
    original = Image.open('bw.gif')
    bg = original.resize((116, 56), Image.NEAREST)
    ext = ".tif"
    bg.save("input-NEAREST" + ext)
    image = Image.open('input-NEAREST.tif')
    captcha_string =  image_to_string(image).replace(" ","").replace("\n","").replace("%","8").replace('\N','W').replace('l/','V')
    print captcha_string
    host = domain[7:len(domain)-1]
    headers = {
    'Host': host,
    'Connection': 'keep-alive',
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:27.0) Gecko/20100101 Firefox/27.0',
    'Content-type': 'application/x-www-form-urlencoded',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Referer': comment_link,
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-US,en;q=0.5',
    }
    Send = [line.strip() for line in open('Send')]
    data = {
            'name': Unames[randint(0,len(Unames)-1)]+str(randint(65,99)),
            'email': '',
            'komentar': comment,
            'captcha_image':'/'+relative_image_link,
            'captcha_attempt':captcha_string,
    }
    data = urllib.urlencode(data)
    data = data +'&submit=Po%9Aalji' 
    print data 
    req = urllib2.Request(comment_link, data, headers) 
    response = urllib2.urlopen(req)
    print response.getcode()
    the_page = response.read()
    soup=BeautifulSoup(the_page)
    print soup
    
    
    
