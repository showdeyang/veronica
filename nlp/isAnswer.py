# -*- coding: utf-8 -*-
#This script trains a model that determines whether a sentence can answer a given question well.
import json
import numpy as np
import math
import re
import jieba
import random
import matplotlib.pyplot as plt 

with open('./baidu_zhidao.json','r') as f:
    data = json.loads(f.read())

rawData = []
for qa in data:
    q = qa['q']
    if 'ans' in qa.keys():
        if len(qa['ans']) > 0:
            ans = [item['a'].replace('展开全部','') for item in qa['ans']]
    rawData.append([q,ans])
    
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

def prepareX(pair, ID):
    #this only prepares a row of X for a (q,a)-pair.
    q,a = pair[0], pair[1]
    qc,ac = list(jieba.cut(q)), list(jieba.cut(a))
    row = [relevance(qc,ac), depth(qc,ac), len(qc), len(ac), ID]
    return row

def goodPairs(rawData):
    results = []
    for qa in rawData:
        for i in range(len(qa[1])):
            pair = [qa[0], qa[1][i]] 
            results.append(pair)
    return results
    
def badPairs(rawData,n=len(rawData)):
    results = []
    for i in range(n):
        c = random.choices(rawData,k=2)
        data1,data2 = c[0],c[1]
        q,a = data1[0],random.choice(data2[1])
        pair = [q,a]
        results.append(pair)
    return results

test_ratio = 0.3
train_ratio = 1 - test_ratio
n = len(rawData) #the number of questions

gP,bP = goodPairs(rawData), badPairs(rawData)
random.shuffle(gP)
random.shuffle(bP)

gpi,bpi = int(len(gP)*train_ratio), int(len(bP)*train_ratio)
test_set_good, test_set_bad = gP[gpi:], bP[bpi:]
train_set_good, train_set_bad = gP[:gpi], bP[:bpi]

train_dataset = []
test_dataset = []

for i in range(len(train_set_good)):
    train_dataset.append( prepareX(train_set_good[i],i) + [train_set_good[i][0], train_set_good[i][1], 1] )
for j in range(len(train_set_bad)):
    i = len(train_set_good)
    train_dataset.append( prepareX(train_set_bad[j],i+j) + [train_set_bad[j][0], train_set_bad[j][1], 0] )  
    
for i in range(len(test_set_good)):
    test_dataset.append( prepareX(test_set_good[i],i) + [test_set_good[i][0], test_set_good[i][1], 1] )
for j in range(len(test_set_bad)):
    i = len(test_set_good)
    test_dataset.append( prepareX(test_set_bad[j],i+j) + [test_set_bad[j][0], test_set_bad[j][1], 0] )  

random.shuffle(train_dataset)
random.shuffle(test_dataset)

########################################
#training

# Create data
N = 500
x = np.random.rand(N)
y = np.random.rand(N)
colors = (0,0,0)
area = np.pi*3

# Plot
plt.scatter(x, y, s=area, c=colors, alpha=0.5)
plt.title('Scatter plot pythonspot.com')
plt.xlabel('x')
plt.ylabel('y')
plt.show()



