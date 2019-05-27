# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import re
import json
import jieba
import random
import glob
import numpy as np 
import math
with open('./baidu_zhidao.json','r') as f:
    data = json.loads(f.read())

rawData = []
for qa in data:
    q = qa['q']
    if 'ans' in qa.keys():
        if len(qa['ans']) > 0:
            ans = [item['a'].replace('展开全部','') for item in qa['ans']]
            for a in ans:
                rawData.append([q,a])

print('extracting data from baidu_zhidao scraper')  
rawConvFolder = '/data/clean_chat_corpus/'
convFiles = glob.glob(rawConvFolder + '*.tsv')
print(convFiles)

data = []
for convFile in convFiles:
    print('extracting', convFile)
    formattedData = []
    with open(convFile,'r') as f:
        rows = f.readlines()
        for row in rows:
            #if len(row.split('\t')) == 2:
            formattedData.append(row.split('\t'))
            #print(row)
        
        data += formattedData
#    


#formattedData = []
#with open('/data/clean_chat_corpus/qingyun.tsv','r') as f:
#    rows = f.readlines()
#    for row in rows:
#        #if len(row.split('\t')) == 2:
#        formattedData.append(row.split('\t'))
#        #print(row)
#    
#    data += formattedData    
#
rawData += data


questions = [row[0] for row in rawData]
answers = [row[1] for row in rawData]

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

def cosineDistance(q,a):
    chars = list(set(q+a))
    u,v = [], []
    for char in chars:
        count = 0
        for c in q:
            if char == c:
                count += 1
        u.append(count)
    
        count = 0
        for c in a:
            if char == c:
                count += 1
        v.append(count)
        
    u = np.array(u)
    v = np.array(v)
    if np.sum(u) * np.sum(v) == 0:
        return 0
    return np.dot(u,v)/(np.sqrt(np.dot(u,u))*np.sqrt(np.dot(v,v)))

def prepareAnswers(query,questions=questions,answers=answers,mode=0,threshold=0.8):
    
    results = []
    if mode == 0:
        queryC = list(jieba.cut(query))
        for q in questions:
            
            qc = list(jieba.cut(q))
            s = 1*(relevance(queryC,qc) ) #+ depth(queryC,qc)
            if s >= threshold:
                result = answers[questions.index(q)]
                results += result
        
    if mode == 1:
        queryC = list(jieba.cut(query))
        for ans in answers:
            for a in ans:
                ac = list(jieba.cut(a))
                s = 0.5*(relevance(queryC,ac) + depth(queryC,ac))
                if s >= threshold:
                    results.append(a)
    if mode == 2:
        queryC = list(jieba.cut(query))
        for q in questions:
            qc = list(jieba.cut(q))
            s = 0.5*(relevance(queryC,qc) + depth(queryC,qc))
            if s >= threshold:
                result = answers[questions.index(q)]
                results += result
        for ans in answers:
            for a in ans:
                ac = list(jieba.cut(a))
                s = 0.5*(relevance(queryC,ac) + depth(queryC,ac))
                if s >= threshold:
                    results.append(a)
                    
    if mode == 3:
        for q in questions:
            
            s = cosineDistance(query,q)
            if s >= threshold:
                result = answers[questions.index(q)]
                results.append(result)
    if mode ==4:
        for ans in answers:
            for a in ans:
                s = cosineDistance(query,q)
                if s >= threshold:
                    results.append(a)
    return results


    
    
def reply(query,questions=questions,answers=answers, mode=3, threshold=0.9, attempts=100000):
    results = []
    for i in range(attempts):
        q = random.choice(questions)
        s = cosineDistance(query,q)
        #s = (qInA(query,q)*len(query) + qInA(q,query)*len(q))/2.0
        if s >= threshold:
            ind = questions.index(q)
            result = answers[ind]
            results.append(result)
            if len(results) > 3:
                break
    
    #results = prepareAnswers(query,questions=questions,answers=answers,mode=mode,threshold=0.5)
    if len(results) == 0:
        return '对不起，我现有的知识还无法很好的回答此问题．'
    else:
        fitness =[ cosineDistance(res,q) for res in results]
        maxF = np.max(fitness)
        ans = results[fitness.index(maxF)]
        #ans = random.choice(results)
        #print(results)
        #print(ans)
        return ans

#def determinePoissonMean(size=1000,questions=questions):
print('questions',len(questions))
print('conversation starts')
query = input('>>>')
while query != 'bye veronica':
    if query.strip() == '':
        query = input('>>>')
    else:
        print(reply(query).strip())   
    query = input(">>>")   
