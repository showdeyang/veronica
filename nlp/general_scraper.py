# -*- coding: utf-8 -*-
from requests_futures.sessions import FuturesSession
import time
import configparser
import json
#import hashlib
import requests
from bs4 import BeautifulSoup
import random
import re
import jieba
import math

sleep_time = 0.05
hdrs = [{
        "connection": "keep-alive",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36",
        "accept": "*/*",
        "accept-encoding": "gzip, deflate",
        "accept-language": "zh-CN,zh;q=0.9",
        "cache-control": "no-cache"
        },
        {
        "connection": "keep-alive",
        "user-agent": "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36",
        "accept": "*/*",
        "accept-encoding": "gzip, deflate",
        "accept-language": "zh-CN,zh;q=0.9",
        "cache-control": "no-cache"
        },
        {
        "connection": "keep-alive",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) Chrome/62.0.3202.94 Safari/537.36",
        "accept": "*/*",
        "accept-encoding": "gzip, deflate",
        "accept-language": "zh-CN,zh;q=0.9",
        "cache-control": "no-cache"
        },
        {
        "connection": "keep-alive",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) Safari/537.36",
        "accept": "*/*",
        "accept-encoding": "gzip, deflate",
        "accept-language": "zh-CN,zh;q=0.9",
        "cache-control": "no-cache"
        },
        {
        "connection": "keep-alive",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) Chrome/62.0.3202.94",
        "accept": "*/*",
        "accept-encoding": "gzip, deflate",
        "accept-language": "zh-CN,zh;q=0.9",
        "cache-control": "no-cache"
        },
        {
        "connection": "keep-alive",
        "user-agent": "Chrome/62.0.3202.94 AppleWebKit/537.36 (KHTML, like Gecko)",
        "accept": "*/*",
        "accept-encoding": "gzip, deflate",
        "accept-language": "zh-CN,zh;q=0.9",
        "cache-control": "no-cache"
        },
        {
        "connection": "keep-alive",
        "user-agent": "AppleWebKit/537.36 (KHTML, like Gecko) Safari/537.36",
        "accept": "*/*",
        "accept-encoding": "gzip, deflate",
        "accept-language": "zh-CN,zh;q=0.9",
        "cache-control": "no-cache"
        },
        {
        "connection": "keep-alive",
        "user-agent": "AppleWebKit/537.36 (KHTML, like Gecko) Mozilla/5.0 (Windows NT 10.0; WOW64)",
        "accept": "*/*",
        "accept-encoding": "gzip, deflate",
        "accept-language": "zh-CN,zh;q=0.9",
        "cache-control": "no-cache"
        },
        {
        "connection": "keep-alive",
        "user-agent": "AppleWebKit/537.36 (KHTML, like Gecko) Mozilla/5.0 (Windows NT 10.0; WOW64) Safari/537.36",
        "accept": "*/*",
        "accept-encoding": "gzip, deflate",
        "accept-language": "zh-CN,zh;q=0.9",
        "cache-control": "no-cache"
        },
        {
        "connection": "keep-alive",
        "user-agent": "Chrome/62.0.3202.94 Safari/537.36",
        "accept": "*/*",
        "accept-encoding": "gzip, deflate",
        "accept-language": "zh-CN,zh;q=0.9",
        "cache-control": "no-cache"
        }]
def iterateRequest(url, headers=random.choice(hdrs), count=0):
    try:
        #sleepTime= 10
        print('sleep',10)
        result = requests.get(url, headers=headers)
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        #
        print(e)
        print('retry count', count)
        #print('sleep', sleepTime)
        time.sleep(10)
        
        result = iterateRequest(url, headers=random.choice(hdrs), count=count+1)
    if 'com/error' in result.url:
        result = iterateRequest(url, headers=random.choice(hdrs), count=count+1)
    return result

def _async_requests(urls, headers=hdrs, mode=0):

    session = FuturesSession(max_workers=50)
    futures = []
#    urls.remove(None)
    #print(urls)
    for url in urls: 
        #print('requests sent: ', '(', urls.index(url),'/', len(urls),')')
        if 'http:' in url or 'https:' in url:
            #time.sleep(random.random()*0.05)
            if mode==1:
                time.sleep(sleep_time*2)
            else:
                time.sleep(0)
            try:
                print('sending request:' , urls.index(url)+1, 'out of', len(urls))
                d = session.get(url, headers=random.choice(hdrs))
                
            except ConnectionError:
                d = None
            if d is not None:
                futures.append(d)
        
        
        #[session.get(url, headers=headers) for url in urls]
    responses = []
    for future in futures:
        print(len(futures))
        print('responses received: ', '(', futures.index(future)+1,'/', len(futures),')\n')
        try:
            res = future.result()
        except requests.exceptions.RequestException as e:  # This is the correct syntax
            print(e)
            continue
            #res = iterateRequest(urls[futures.index(future)])
        if 'error' in res.url:
            res = iterateRequest(urls[futures.index(future)])
            
        responses.append(res)
        print(res.url)
        #[session.get(url, headers=headers) for url in urls]
            
    return responses

def scrape(query, headers=hdrs, pages=3):
    urls = []
    for page in range(pages):
        if page == 0:
            urls.append('https://www.baidu.com/s?wd='+ query.strip())
        else:
            urls.append('https://www.baidu.com/s?wd=' + query.strip() + '&pn=' + str(page) + '0')

    responses = _async_requests(urls, headers=hdrs)
    soups = []
    urls = []
    for response in responses:
        #print('scraped ', response.url)
        #print('response headers', response.headers)
        html = response.content
        #filename = response.url.replace('https://','').replace('http://','').replace('.com/','.com--').replace('%0A','') + '.html'
        soup = BeautifulSoup(html,'lxml')
        soups.append(soup)
        for link in soup.findAll('a'):
            try:
                urls.append(link['href'])
            except KeyError:
                pass
        #urls += [link['href'] for link in soup.findAll('a')]
    urls = list(set(urls))
    return soups,urls

def parse(soups):
    #returns sentences
    sentences = []
    for soup in soups:
        elems = soup.findAll('p') + soup.findAll('div', {'class':re.compile('content')}) + soup.findAll('div', {'class':re.compile('para')}) + soup.findAll('div', {'class':re.compile('article')}) + soup.findAll('div', {'class':re.compile('answer')}) + soup.findAll('div', {'class':re.compile('Content')}) + soup.findAll('div', {'class':re.compile('Para')}) + soup.findAll('div', {'class':re.compile('Answer')}) + soup.findAll('div', {'class':re.compile('Article')})
        
        
        for elem in elems:
            ss = elem.text.split('\n')
            for s in ss:
                s = s.replace('。','。@@@').replace('？','？@@@').replace('?','?@@@').replace('..','..@@@').replace('。。','。。@@@').replace('\t',' ').replace('\r','').replace('|',' ')
                s = re.sub(r'\ *','',s)
                l = s.split('@@@')
                sentences += l
    
    return sentences

def relevance(qc,ac):
    c = 0 
    for x in qc:
        if x in ac:
            c += 1
    if len(qc) == 0:
        return 0
    else:
        return c/len(qc)

def depth(qc,ac):
    c = 0 
    for x in ac:
        if x in qc:
            c += 1
    if len(ac) == 0:
        return 0
    else:
        return c/len(ac)
    
def relevance2(qc,ac):
    qc = [item for item in qc if len(item)>=2]
    ac = [item for item in ac if len(item)>=2]
    c = 0 
    for x in qc:
        if x in ac:
            c += 1
    if len(qc) == 0:
        return 0
    else:
        return c/len(qc)

def depth2(qc,ac):
    qc = [item for item in qc if len(item)>=2]
    ac = [item for item in ac if len(item)>=2]
    c = 0 
    for x in ac:
        if x in qc:
            c += 1
    if len(ac) == 0:
        return 0
    else:
        return c/len(ac)

def qInA(q,a):
    c = 0
    for char in q:
        if char in a:
            c += 1
    if len(q) == 0:
        return 0
    else:
        return c/len(q)
    
def aInQ(q,a):
    c = 0
    for char in a:
        if char in q:
            c += 1
    if len(a) == 0:
        return 0
    else:
        return c/len(a)

def score(qc,ac):
    return relevance(qc,ac)*depth(qc,ac)

def score2(qc,ac):
    return relevance2(qc,ac)*depth2(qc,ac)


query = '谁发现美国大陆'
soups, urls = scrape(query,pages=1)
#soups = [BeautifulSoup(response.content,'lxml') for response in _async_requests(urls)]
sentences = parse(soups)
sentences = list(filter(None, sentences))
for sentence in sentences:
    if sentence == ' ':
        sentences.remove(sentence)
    
sentences = list(set(sentences))

qc = list(jieba.cut(query))
fitness = []
for sentence in sentences:
    ac = list(jieba.cut(sentence))
    fitness.append(math.fabs(0.5-score2(qc,ac)))

ind = fitness.index(min(fitness))
answer = sentences[ind]
print(answer)