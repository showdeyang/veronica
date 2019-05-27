# -*- coding: utf-8 -*-
import numpy as np 
import json
import re
import glob
import random 

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



#with open('./baidu_zhidao.json','r') as f:
#    data = json.loads(f.read())
#
#rawData = []
#for qa in data:
#    q = qa['q']
#    if 'ans' in qa.keys():
#        if len(qa['ans']) > 0:
#            ans = [item['a'].replace('展开全部','') for item in qa['ans']]
#            for a in ans:
#                if len(a) > 0:
#                    rawData.append([q,a])
#
#print('extracting data from baidu_zhidao scraper')  
#rawConvFolder = '/data/clean_chat_corpus/'
#convFiles = glob.glob(rawConvFolder + '*.tsv')
#print(convFiles)
#
#data = []
#for convFile in convFiles:
#    print('extracting', convFile)
#    formattedData = []
#    with open(convFile,'r') as f:
#        rows = f.readlines()
#        for row in rows:
#            #if len(row.split('\t')) == 2:
#            formattedData.append(row.split('\t'))
#            #print(row)
#        
#        data += formattedData
#
#rawData += data
#
#questions = [row[0] for row in rawData]
#answers = [row[1] for row in rawData]

#chars = []
#
#for question in questions:
#    for c in question:
#        chars.append(c)
#
#chars = list(set(chars))
#charCount = len(chars)
#print(chars)
#with open('./chars.json','w') as f:
#    f.write(json.dumps(chars))
####################################################################
    
with open('./chars.json','r') as f:
    chars = json.loads(f.read())


n_classes = 100
stringSize = 10

genes = []
for i in range(n_classes):
    cs = random.choices(chars,k=stringSize)
    gene = ''
    for c in cs:
        gene += c
    genes.append(gene)

qs = list(set(questions))

classes = {} 
for q in qs:
    print('processing question', qs.index(q)+1, 'out of', len(qs))
    d = [cosineDistance(q,gene) for gene in genes]
    g = genes[genes.index(min(genes))]
    if g in classes.keys():
        classes[g].append(q)
    else:
        classes[g] = [q]





