# -*- coding: utf-8 -*-
import numpy as np 
import json
import re
import glob

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

model = {}

for ind in range(len(questions)):
    print('processing question', ind+1 , 'out of', len(questions))
    question = questions[ind]
    
    for i in range(len(question)-4):
        #print(question)
        #print(i, question[i])
        if question[i:i+5] in model.keys():
            #print([answers[ind]])
            #print(answers[ind][0])
            model[question[i:i+5]].append(answers[ind][0])
        else: 
            model[question[i:i+5]] = [answers[ind][0]]


for ind in range(len(answers)):
    print('processing answer', ind+1, 'out of', len(answers))
    answer = answers[ind]
    for i in range(len(answer)):
        if i != len(answer)-1:
            if answer[i] in model.keys():
                model[answer[i]].append(answer[i+1])
            else:
                model[answer[i]] = [answer[i+1]]
        else:
            if answer[i] in model.keys():
                model[answer[i]].append('EOS')
            else:
                model[answer[i]] = ['EOS']


def most_common (lst):
    return max(((item, lst.count(item)) for item in set(lst)), key=lambda a: a[1])[0]
        
def reply(question,model=model):
    answer = ''
    while 'EOS' not in answer:
        
        v = []
        for i in range(len(question)-4):
            if question[i:i+5] in model.keys():
                v += model[question[i:i+5]]
        for char in answer:
            if char in model.keys():
                v += model[char]
        a = most_common(v)
        
        answer += a
        print(answer)
    return answer

question = input('>>>')
while question != 'bye veronica':
    if question.strip() != '':
        answer = reply(question, model)
    print(answer)
    question = input('>>>')
    
    
    

