#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 27 15:51:47 2021

@author: nidhisinha
"""

import sys, re, pprint 

pp = pprint.PrettyPrinter(indent = 5, width = 4, depth = 4) 
#number of occurences of POS in corpus, {POS: NUM}
pos_num = {}
#number of occurences of word as POS in corpus, {WORD{POS:NUM}}
word_pos_num = {}
#number of occurences of word in corpus, {WORD:NUM}
word_num = {}
#number of occurences of POS following another POS in corpus, {CURRENT_POS: {NEXT_POS : COUNT, TOTAL_OCCURENCES : COUNT_2}}
trans_dict = {} 
#OOV POS 
oov_num = {} 
#threshold of oov words
OOV_THRESHOLD = 1
#counter for oov words
OOV_COUNT = 0
#constnat of oov words
OOV_CONSTANT = 0.0001 

TOTAL_OCCURRENCES = '_TOTAL_OCCURRENCES_OF_KEY'
TRANSITION_FREQ = 'TRANSITION_FREQ'

def emissionCounter(word, pos):
    curr_freq = word_pos_num.get(word, {pos:0})
    curr_freq[pos] = curr_freq.get(pos, 0) + 1
    word_pos_num[word] = curr_freq
    pos_num[pos] = pos_num.get(pos, 0) + 1 
    word_num[word] = word_num.get(word, 0) + 1

def transitionCounter(curr_pos, next_pos):
    curr_freq= trans_dict.get(curr_pos, {next_pos: 0})
    curr_freq[next_pos] = curr_freq.get(next_pos, 0) + 1 
    curr_freq[TOTAL_OCCURRENCES] = curr_freq.get(TOTAL_OCCURRENCES, 0 ) + 1 
    trans_dict[curr_pos] = curr_freq 
def transitionFrequency():
    for curr_pos, next_pos_dict in trans_dict.items():
        total = next_pos_dict[TOTAL_OCCURRENCES]
        for next_pos, count in next_pos_dict.items():
            if next_pos == TOTAL_OCCURRENCES:
                continue 
            next_pos_dict[next_pos] = next_pos_dict[next_pos]/total 
            trans_dict[curr_pos] = next_pos_dict
def emissionFrequency(): 
    global OOV_COUNT
    for word, pos_num1 in word_pos_num.items():
        for pos, num in pos_num1.items():
            if word_num[word] <= OOV_THRESHOLD:
                OOV_COUNT += 1
                oov_num[pos] = oov_num.get(pos, 0) + 1
            pos_num1[pos] = num / pos_num[pos]
            word_pos_num[word] = pos_num1
def OOVFrequency():
    for pos in pos_num.keys():
        val = oov_num.get(pos, False)
        if val:
            oov_num[pos] = val/OOV_COUNT 
        else: 
            oov_num[pos] = OOV_CONSTANT 

def train(file):
    p = '(.+)\t(.+)|(\n)'
    pattern = re.compile(p)
    with open(file) as trainingfile:
        prev_pos = ''
        word = ''
        curr_pos = '' 
        for i, line in enumerate(trainingfile):
            match = pattern.search(line)
            if match[3]:
                word = ''
                curr_pos = ''
            else:
                word = match[1]
                curr_pos = match[2]
                emissionCounter(word, curr_pos)
                transitionCounter(prev_pos, curr_pos)
                prev_pos = curr_pos
    pp.pprint(trans_dict[''])
    
    
def findFrequencies():
    emissionFrequency()
    transitionFrequency()
    OOVFrequency()
    
def emissionProb(word): 
    scores = word_pos_num.get(word, False)
    if scores:
        return scores 
    return oov_num

def transitionProb(prev_pos, curr_pos):
    return trans_dict[prev_pos].get(curr_pos, 0)

def sentenceProcesser(sent):
    lookup = [{} for x in sent]
    lookup[0] = {'': 1}
    lookup[len(sent) - 1] = {'':1}
    ans = []
    for i, word in enumerate(sent):
        if i == 0 or i == len(sent)- 1:
            continue
        score_dict = {} 
        best_score = -1 
        emission_score = emissionProb(word)
        for guess, emission_prob in emission_score.items():
            for prev_pos, prev_score in lookup[i - 1].items():
                prob = prev_score * emission_prob * transitionProb(prev_pos, guess)
                score_dict[guess] = prob
                if prob > best_score: 
                    best_score = prob 
                    likely_pos = guess 
        lookup[i] = score_dict
        ans.append((word, likely_pos))
    return ans
 
def test(testfilename, outputfilename):
    with open(testfilename) as testfile:
        with open(outputfilename, 'w') as outputfile:
            sent = ['']
            for i, line in enumerate(testfile):
                if re.match('^\n$', line):
                    sent.append('')
                    p = sentenceProcesser(sent)
                    for label in p:
                         outputfile.write(f'{label[0]}\t{label[1]}\n')
                    outputfile.write('\n')
                    sent = ['']
                    continue
                sent.append(line.strip())

def run(trainingfile, testfile, outputfile):
    for name in trainingfile:
        train(name)
    findFrequencies()
    for i, name in enumerate(testfile):
        test(name, outputfile[i])

def main(): 
    training_files = ['WSJ_24.pos', 'WSJ_02-21.pos']
    test_files = ['WSJ_23.words']
    output_files = []
    if len(sys.argv) > 1:
        if sys.argv[1] == '-t':
            training_files.pop(1)
        elif sys.argv[1] == '-d':
            training_files.pop(0)
            test_files.pop(0)
        elif sys.argv[1] == '-test':
            test_files = ['WSJ_23.words']
            output_files = ['submission.pos']
            run(training_files, test_files, output_files)
            return
        else: 
            training_files = [sys.argv[1]]
    if len(sys.argv) > 2:
        test_files = [sys.argv[2]]
    if len(sys.argv) > 3:
        output_files = [sys.argv[3]]
    if len(output_files) == 0:
        for i, name, in enumerate(test_files):
            output_files.append(f'submission.pos')
            
    run(training_files, test_files, output_files)
main()
        
