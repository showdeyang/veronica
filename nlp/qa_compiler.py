# -*- coding: utf-8 -*-
import numpy as np 
import json
import re
import glob
import os 
import multiprocessing
import random
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
                if len(a) > 0:
                    rawData.append([q,a])

print('extracting data from baidu_zhidao scraper')  
rawConvFolder = '/data/clean_chat_corpus/'
convFiles = glob.glob(rawConvFolder + '*.tsv')
print(convFiles)

data = []
removeList = ['/data/clean_chat_corpus/douban_single_turn.tsv','/data/clean_chat_corpus/subtitle.tsv']
if len(removeList) > 0:
    for item in removeList:
        convFiles.remove(item)
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

rawData += data

questions = [row[0] for row in rawData]
answers = [row[1] for row in rawData]
print(len(questions))
#
#model = {}

#for ind in range(len(questions)):
#    print('processing question', ind+1 , 'out of', len(questions))
#    question = questions[ind]
#    
#    for i in range(len(question)-4):
#        #print(question)
#        #print(i, question[i])
#        if question[i:i+5] in model.keys():
#            #print([answers[ind]])
#            #print(answers[ind][0])
#            model[question[i:i+5]].append(answers[ind][0])
#        else: 
#            model[question[i:i+5]] = [answers[ind][0]]


#for ind in range(len(answers)):
#    print('processing answer', ind+1, 'out of', len(answers))
#    answer = answers[ind]
#    for i in range(len(answer)):
#        if i != len(answer)-1:
#            if answer[i] in model.keys():
#                model[answer[i]].append(answer[i+1])
#            else:
#                model[answer[i]] = [answer[i+1]]
#        else:
#            if answer[i] in model.keys():
#                model[answer[i]].append('EOS')
#            else:
#                model[answer[i]] = ['EOS']

  

def most_common(lst):
    x = max(((item, lst.count(item)) for item in set(lst)), key=lambda a: a[1])[0]
    return x
        
#def reply(question,model=model):
#    answer = ''
#    while 'EOS' not in answer:
#        
#        v = []
#        for i in range(len(question)-4):
#            if question[i:i+5] in model.keys():
#                v += model[question[i:i+5]]
#        for char in answer:
#            if char in model.keys():
#                v += model[char]
#        a = most_common(v)
#        
#        answer += a
#        print(answer)
#    return answer

def split2g(sentence):
    l = len(sentence)
    twogram = []
    for i in range(l-1):
        twogram.append(sentence[i:i+2])
    return twogram

def analyze2gq(question):
    print('analyze question', questions.index(question)+1)
    twograms =  split2g(question)
    for twogram in twograms:
        #print(twogram)
        with open('./twograms/' + twogram.replace('/','-') + '.txt', 'a') as f:
            print(question,file=f)
    return 1

def removeFrequent2g(file):
    with open(file,'r') as f:
        lines = [d.strip() for d in f.readlines()]
        lines = list(set(lines))
        if len(lines) > 10000:
            os.remove(file)
            print('removed', file)
    with open(file,'w') as f:
        [print(line, file=f) for line in lines]
    return 1

def search_binary_with_comprehension (xs, target):
   return [ count  for count, val in enumerate(xs) if val == target]


def analyze2gqs(questions):
    pool = multiprocessing.Pool()
    
    print(len(questions))
    
    r = pool.map(analyze2gq,questions)
    
    
    
    #remove frequent twograms
    files = glob.glob(r'./twograms/*.txt')
    
    r = pool.map(removeFrequent2g, files)
                
    



def similarQ(query,p=10,multi=False):
    pool = multiprocessing.Pool(p)
    q = split2g(query)
    results = []
    for c in q:
        try:
            with open('./twograms/' + c + '.txt', 'r') as f:
                results += [d.strip() for d in f.readlines()]
        except FileNotFoundError:
            continue
    if multi:
        try:
            random.shuffle(results)
            size = 1000
            partitions = range(math.ceil(len(results)/size))
            subresults = []
            for partition in partitions:
                subresults.append(results[partition*size:(partition+1)*size])
            modes = pool.map(most_common, subresults)
            result = most_common(modes)
        except ValueError:
            result = None
    else:
        try:
            result = most_common(results)
        except ValueError:
            result = None
    #print(result)
    return result

def replyFast(query):
    result = similarQ(query, multi=True)
    if result:
        indexes = search_binary_with_comprehension(questions,result)
        results = [answers[ind] for ind in indexes]
        
        try:
            return random.choice(results)
        except IndexError:
            result = similarQ(query,multi=False)
            if result:
                indexes = search_binary_with_comprehension(questions,result)
                results = [answers[ind] for ind in indexes]
                return random.choice(results)
            else: 
                return None
    else:
        return None

def removeDup2g(p=6):
    pool = multiprocessing.Pool(p)
    files = glob.glob(r'./twograms/*.txt')
    
    r = pool.map(removeFrequent2g, files)
    
#analyze2gqs(questions) 
#removeDup2g()

question = input('>>>')
while question != 'bye veronica':
    if question.strip() != '':
        answer = replyFast(question)
    print(answer)
    question = input('>>>')
#    
    
    

