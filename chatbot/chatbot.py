# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import requests
import numpy as np
import random
import math
import json
import time
from multiprocessing import Pool
from requests_futures.sessions import FuturesSession
from concurrent.futures import ThreadPoolExecutor
import jieba


#session = FuturesSession(executor=ThreadPoolExecutor(max_workers=12))

def inclusion(query, question):
    count = 0
    for char in query:
        if char in question:
            count += 1
    return count

def _async_requests(urls):
    """
    Sends multiple non-blocking requests. Returns
    a list of responses.
 
    :param urls:
        List of urls
    """
     
    session = FuturesSession(max_workers=50)
    futures = [session.get(url) for url in urls]
    return [future.result() for future in futures]

def lenDiff(query,question):
    return len(question) - len(query)

def qbadness(query,question):
    badness = len(question) + len(query) - 2*inclusion(query,question)
    return badness

def parallelScrape(queryUrls):
    results = []
    responses = _async_requests(urls)
    
    for response in responses:
        
        soup = BeautifulSoup(response.content,'lxml')
        question = questions[responses.index(response)]
        #question = soup.find("span",{"class":"ask-title"}).get_text()
        answerElems = soup.findAll("div",{"accuse":"aContent"})
        
        #timesElem = [elem.get_text() for elem in soup.findAll("span",{"class":"wgt-replyer-all-time"})]
        #times = [elem.replace('推荐于','').replace('\n','') for elem in timesElem]
        
        #likesElem = soup.findAll('span',{'alog-action':'qb-zan-btnbestbox'}) + soup.findAll('span',{'alog-action':'qb-zan-btn'}) 
        #likes = [elem['data-evaluate'] for elem in likesElem]
        
        #commentElem = soup.findAll('span',{'alog-action':'qb-comment-btnbestbox'}) + soup.findAll('span',{'alog-action':'qb-comment-btn'}) 
        
        answers = []
        for answerElem in answerElems:
            answer = answerElem.get_text().strip().replace('\n','').replace('展开全部','')
            answers.append(answer)
        #resultDict = {'q': question, "a": answers, 't': times, 'l': likes}
        resultDict = {'q': question, "a": answers}
        results.append(resultDict)
    return results

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

def score(qc,ac):
    return 0.25-(0.5 - depth(qc,ac)*relevance(qc,ac))**2
    

#
#with open('./fitness.model','r') as f:
#        model = f.read()
#        print(model)
#        geneMean = json.loads(model)

queryUrlPrefix = 'https://zhidao.baidu.com/search?word='
query = input(">>>")
if query == 'bye lily':
        print("下次再聊！")
while query != 'bye lily':
    time1 = time.time()
    if query is '':
        query = input(">>>")
    if query == 'bye lily':
        print("下次再聊！")
        break
    queryUrl = queryUrlPrefix + query
    
    #Get result urls
    html = requests.get(queryUrl).content
    soup = BeautifulSoup(html,"lxml")
    elems = soup.find("div",{"class":"list-inner"}).findAll("dt",{"class":"dt mb-4 line"})
    urls = [elem.a['href'] for elem in elems]
    questions = [elem.a.get_text() for elem in soup.findAll('dt',{'class':'dt mb-4 line'})]
    
#    queryUrl = queryUrlPrefix + query + '&pn=10'
#    
#    #Get result urls
#    html = requests.get(queryUrl).content
#    soup = BeautifulSoup(html,"lxml")
#    elems = soup.find("div",{"class":"list-inner"}).findAll("dt",{"class":"dt mb-4 line"})
#    urls += [elem.a['href'] for elem in elems]
#    questions += [elem.a.get_text() for elem in soup.findAll('dt',{'class':'dt mb-4 line'})]
#    
#    queryUrl = queryUrlPrefix + query + '&pn=20'
#    
#    #Get result urls
#    html = requests.get(queryUrl).content
#    soup = BeautifulSoup(html,"lxml")
#    elems = soup.find("div",{"class":"list-inner"}).findAll("dt",{"class":"dt mb-4 line"})
#    urls += [elem.a['href'] for elem in elems]
#    questions += [elem.a.get_text() for elem in soup.findAll('dt',{'class':'dt mb-4 line'})]
    #print(urls)
#    queryUrls = []
#    questions = [elem.a.get_text() for elem in soup.findAll('dt',{'class':'dt mb-4 line'})]
#    
#    #print(questions)
#    
#    qbad = [qbadness(query,question) for question in questions]
#    #if len(qbad) == 0:
#        
#    #qbmax = np.max(qbad)
#    #qsInd = qbad.index(qbmax)
#    
#    for i in range(len(qbad)):
#        if qbad[i] <= np.percentile(qbad,100):
#            queryUrls.append(urls[i])
    queryUrls = urls
    #print('urls:',len(queryUrls))
#    queryUrls.append(urls[qsInd])
    #print(queryUrls)
    
    #Crawl each url, to generate (q,a).
    #results = []
    time2 = time.time()
    #######Scraping Urls ################
#    
#    with Pool() as p:
#        results = p.map(parallelScrape,url,queryUrls)
#        #resultDict = parallelScrape(url,queryUrls)
#        #results.append(resultDict)
#        #print(resultDict)
    results = parallelScrape(queryUrls)
    time3 = time.time()    
    
    #############################################
    #Now all possible QAs are in resultDict. Analyse resultDict to get the best reply answer.
    #First decide which question is relevant.
    replies = []
    for result in results:
        for ans in result['a']:
            
            ind = result['a'].index(ans)
            replies.append({'q': result['q'], "a": ans})
    
    #Now we have replies, map replies to features, and then apply reinforcement learning.
    time4 = time.time()
    #gene = [np.random.normal(g,0) for g in geneMean]
    #gene = geneMean
    # + g*random.random()
    #features=  []
    fitnesses = [] 
    for reply in replies:
        
        ind = replies.index(reply)
        #print(ind)
        #feature = []
        #qbad = qbadness(query,reply['q'])
        #print(reply['l'])
        #like = int(reply['l'])
        
        #if len(reply['a']) == 0:
        #    alen = 10000
        #else: 
         #   alen = 0.01*(len(reply['a'])**2)
        
        #infodiff = 0 if math.fabs(len(reply['a']) - len(query)) < 10 else math.fabs(len(reply['a']) - len(query)) 
        #ainc = inclusion(reply['a'],query) if inclusion(reply['a'],query) < 10 else 10
        #rtime = reply['t'].split('-')
        #print(time)
#        try:
#            elapse = int(rtime[0]) + int(rtime[1])/12.0 + int(rtime[2])/366.0 - 2018
#        except ValueError:
#            elapse = 0
#        #print(elapse)
#        feature = [qbad,like,alen,infodiff,ainc,elapse]
        q = query
        a = reply['a']
        qc,ac = list(jieba.cut(q)), list(jieba.cut(a))
        fitness = score(qc,ac)
#        fitness = np.matmul(gene,feature)
        fitnesses.append(fitness)
        print('---------------------')
        #print("Feature:",feature)
        print('Fitness:',fitness)
        print('Q:',reply['q'])
        print('A:',reply['a'])
        
        print(fitnesses)
    print(fitnesses)
    print('#######最后选择的答案######')
    print('fitness',)
    try:
        maxFit = random.choice([fit for fit in fitnesses if fit >= np.percentile(fitnesses,85) ])
        
        fitInd = fitnesses.index(maxFit)
        print('fitness',maxFit)
        #print(maxFit, fitInd)
        time5 = time.time()
        tt1 = time2-time1
        tt2 = time3-time2
        tt3 = time4-time3
        tt4 = time5-time4
        #print(tt1,tt2,tt3,tt4)
        #print("Total Time Taken:",tt1+tt2+tt3+tt4)
        print(replies[fitInd]['a'])
    except ValueError:
        print("聊别的吧...")
    query = input('>>>')


    

