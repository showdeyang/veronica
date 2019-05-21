# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import requests
import numpy as np
import random
import math
import json

def inclusion(query, question):
    count = 0
    for char in query:
        if char in question:
            count += 1
    return count

def lenDiff(query,question):
    return len(question) - len(query)

def qbadness(query,question):
    badness = len(question) + len(query) - 2*inclusion(query,question)
    return badness

with open('./fitness.model','r') as f:
        model = f.read()
        print(model)
        geneMean = json.loads(model)

#Randomly take one question from questions.txt, iterate RL for each question.
with open('./questions.txt','r') as f:
    questionSet = f.readlines()

queryUrlPrefix = 'https://zhidao.baidu.com/search?word='
#query = '堕胎应该被合法化吗'
query = random.choice(questionSet).replace('\n','')
print("问： " + query + '\n')
queryUrl = queryUrlPrefix + query

#Get result urls
html = requests.get(queryUrl).content
soup = BeautifulSoup(html,"lxml")
elems = soup.find("div",{"class":"list-inner"}).findAll("dt",{"class":"dt mb-4 line"})
urls = [elem.a['href'] for elem in elems]
#print(urls)
queryUrls = []
questions = [elem.a.get_text() for elem in soup.findAll('dt',{'class':'dt mb-4 line'})]

#print(questions)

qbad = [qbadness(query,question) for question in questions]

for i in range(len(qbad)):
    if qbad[i] < np.mean(qbad):
        queryUrls.append(urls[i])

#print(queryUrls)

#Crawl each url, to generate (q,a).
results = []

for url in queryUrls:
    
    soup = BeautifulSoup(requests.get(url).content,'lxml')
    question = soup.find("span",{"class":"ask-title"}).get_text()
    answerElems = soup.findAll("div",{"accuse":"aContent"})
    
    timesElem = [elem.get_text() for elem in soup.findAll("span",{"class":"wgt-replyer-all-time"})]
    times = [elem.replace('推荐于','').replace('\n','') for elem in timesElem]
    
    likesElem = soup.findAll('span',{'alog-action':'qb-zan-btnbestbox'}) + soup.findAll('span',{'alog-action':'qb-zan-btn'}) 
    likes = [elem['data-evaluate'] for elem in likesElem]
    
    #commentElem = soup.findAll('span',{'alog-action':'qb-comment-btnbestbox'}) + soup.findAll('span',{'alog-action':'qb-comment-btn'}) 
    
    answers = []
    for answerElem in answerElems:
        answer = answerElem.get_text().strip().replace('\n','').replace('展开全部','')
        answers.append(answer)
    resultDict = {'q': question, "a": answers, 't': times, 'l': likes}
    results.append(resultDict)
    #print(resultDict)
    
#Now all possible QAs are in resultDict. Analyse resultDict to get the best reply answer.
#First decide which question is relevant.
replies = []
for result in results:
    for ans in result['a']:
        
        ind = result['a'].index(ans)
        replies.append({'q': result['q'], "a": ans, 't': result['t'][ind], 'l': result['l'][ind]})

#Now we have replies, map replies to features, and then apply reinforcement learning.
variations = 20
genes = [[np.random.normal(g,100) for g in geneMean] for i in range(variations-1)]
genes.append(geneMean)
print('总共%i个变异答案' %variations)
survivors = []
survivorFitnesses = []
for i in range(variations):
    print("第"+str(i+1)+"答")
    gene = genes[i]
    # + g*random.random()
    features=  []
    fitnesses = [] 
    for reply in replies:
        
        ind = replies.index(reply)
        #print(ind)
        feature = []
        qbad = qbadness(query,reply['q'])
        #print(reply['l'])
        like = int(reply['l'])
        alen = len(reply['a'])
        infodiff = math.fabs(alen - len(query))
        ainc = inclusion(reply['a'],query)
        time = reply['t'].split('-')
        try:
            elapse = int(time[0]) + int(time[1])/12.0 + int(time[2])/366.0 
        except ValueError:
            elapse = 0
        #print(elapse)
        feature = [qbad,like,alen,infodiff,ainc,elapse]
        
        fitness = np.matmul(gene,feature)
        fitnesses.append(fitness)
        #print(reply['a'])
        #print(fitness)
        #print(fitnesses)
    #print(fitnesses)
    try:
        maxFit = np.max(fitnesses)
        
        fitInd = fitnesses.index(maxFit)
        #print(maxFit, fitInd)
        #print('#######最后选择的答案######')
        print("Gene", gene)
        print("Fitness", maxFit)
        print(replies[fitInd]['a'])
        print('你觉得这个答案好吗？否=0，是=1')
    except ValueError:
        print("聊别的吧...")
    evaluation = input('>>>')
    if evaluation == "1":
        survivors.append(i)
        survivorFitnesses.append(maxFit)

print('###############################')
#pick the highest fitness score from the survivors
print("Survivors index:",survivors)
print("Survivors Fitness:", survivorFitnesses)
survivalRate = len(survivors)/variations
print("SurvivalRate:",survivalRate)

bestFitness = np.max(survivorFitnesses)
bestFitnessIndex = survivorFitnesses.index(bestFitness)
bestSurvivor = survivors[bestFitnessIndex]
bestGene = genes[bestSurvivor]
#bestReply = replies[bestSurvivor]['a']
print("bestGene:",bestGene)
'''
# + g*random.random()
features=  []
fitnesses = [] 
for reply in replies:
    
    ind = replies.index(reply)
    #print(ind)
    feature = []
    qbad = qbadness(query,reply['q'])
    #print(reply['l'])
    like = int(reply['l'])
    alen = len(reply['a'])
    infodiff = math.fabs(alen - len(query))
    ainc = inclusion(reply['a'],query)
    time = reply['t'].split('-')
    try:
        elapse = int(time[0]) + int(time[1])/12.0 + int(time[2])/366.0 
    except ValueError:
        elapse = 0
    #print(elapse)
    feature = [qbad,like,alen,infodiff,ainc,elapse]
    
    fitness = np.matmul(gene,feature)
    fitnesses.append(fitness)
    #print(reply['a'])
    #print(fitness)
    #print(fitnesses)
#print(fitnesses)

    maxFit = np.max(fitnesses)
    
    fitInd = fitnesses.index(maxFit)
    #print(maxFit, fitInd)
    #print('#######最后选择的答案######')
    print("Gene", bestGene)
    print("Fitness", maxFit)
    print(replies[fitInd]['a'])

'''
with open('./fitness.model','w') as g:
    g.write(json.dumps(bestGene))



