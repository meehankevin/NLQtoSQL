from nltk.corpus import stopwords
from nltk.corpus import wordnet as wn
from nltk.tokenize import word_tokenize
from nltk.tokenize import RegexpTokenizer as regx
from nltk.tokenize import MWETokenizer as mwet
import pandas as pd
import numpy as np
import re

class convertPhrases():

    def __init__(self, keywordsDF, database):
        self.keywordsDF = keywordsDF
        self.database = database

    def getPhraseConversion(self, keywordsDF):

        phrases = {"SELECT COUNT(_)": ['how many', 'get count', 'give count', 'list count'],
                   "SELECT AVG(_)": ['how often', 'get average', 'give average', 'list average'],
                   "SELECT": ['select', 'which', 'what', 'who', 'list', 'get', 'give'],
                   "MAX": ['max', 'maximum', 'highest', 'top', 'best', 'most', 'biggest', 'greatest', 'largest',
                           'ultimate', 'longest'],
                   "MIN": ['min', 'maximum', 'lowest', 'bottom', 'worst', 'least', 'smallest', 'tiniest', 'shortest'],
                   "SUM": ['sum', 'sum total', 'amount', 'quantity', 'aggregate', 'summation', 'tally'],
                   "AVG": ['avg', 'average', 'mean'],
                   "COUNT": ['count', 'mode', 'modal', 'most often', 'most common', 'total', 'frequent', 'most frequent']}
        # issue here:
        # 'which' and 'what' can request either a single or multiple results, depending on if the header is a plural
        # should run check in costructSQl

        for i, row in keywordsDF.iterrows():
            for key, value in phrases.items():
                #print(row['KEYWORD'])
                if row['KEYWORD'] in value:
                    keywordsDF.set_value(i ,'CONVERSION', key)
                    keywordsDF.set_value(i, 'TYPE', "FCN0")
                elif re.search('(\s)(\d+)$' ,row['KEYWORD']): # if keyword ends in a digit
                    # *******************************
                    # later in code, if MAX/MIN come with LIMIT N then
                    # replace MAX with ORDER BY _ DESC LIMIT N
                    # replace MIN with ORDER BY _ LIMIT N
                    # *******************************
                    words = row['KEYWORD'].split()
                    if len(words) == 2 and words[0] in value:
                        keywordsDF.set_value(i, 'CONVERSION',  key + " LIMIT " + words[1])
                elif re.match('(\d+)$', row['KEYWORD']):  # if keyword is a sequence of digits
                    #********************************************
                    # n.b. does not consider dd/mm/yy etc formats
                    # ********************************************
                    res1, res2 = convertPhrases.isPossibleDate(self, row['KEYWORD'], self.database)
                    if len(res1) == 1:
                        keywordsDF.set_value(i, 'CONVERSION', res2)
                        keywordsDF.set_value(i, 'TYPE', "DATE")
                    else:
                        keywordsDF.set_value(i, 'CONVERSION', 'POSSIBLE DATE')
                        keywordsDF.set_value(i, 'TYPE', "DATE0")
                elif row['CONVERSION'] == 'TBC':
                    value1 = [word_tokenize(word) for word in value]
                    tokenizer = mwet([phrase for phrase in value1])
                    keyword = tokenizer.tokenize(row['KEYWORD'].split())
                    for phrase in keyword:
                        if phrase.replace("_", " ") in value:
                            keywordsDF.set_value(i, 'KEYWORD', phrase.replace("_", " "))
                            keywordsDF.set_value(i ,'CONVERSION', key)


        return keywordsDF

    def isPossibleDate(self, phrase, database):
        syns2 = wn.synsets('date')
        res0 = []

        data = pd.read_csv(database, quotechar='"', skipinitialspace=True, encoding='latin1')
        headers = list(data)

        for w1 in headers:
            syns1 = wn.synsets(w1)
            for i in range(len(syns1)):  # i.e. for each word in query
                word1 = wn.synset(syns1[i].name())
                word2 = wn.synset(syns2[5].name())  # synset of 'date' relating to day, month or year
                sim = word1.wup_similarity(word2)
                if not sim is None:
                    if sim > 0.857142:  # lower bound for sim of 'day', 'month', 'year' and 'date'
                        tmp = res0.append(w1)
        if res0 == []:
            for w3 in headers:
                w3 = w3.replace("_", " ").split()
                j = 0
                while j < len(w3):
                    syns3 = wn.synsets(w3[j])
                    for i in range(len(syns3)):  # i.e. for each word in query
                        word3 = wn.synset(syns3[i].name())
                        sim = word3.wup_similarity(word2)
                        if not sim is None:
                            if sim > 0.857142:  # lower bound for sim of 'day', 'month', 'year' and 'date'
                                tmp = res0.append("_".join(w3))
                                j += len(w3)
                    j += 1



        res1 = []
        res2 = ""
        for col in res0:
            if int(phrase.strip()) in list(np.unique(data[col])):
                tmp = res1.append(phrase)
                res2 = col

        return res1, res2

    def stripNonConverted(selfself, keywordsDF):
        keywordsDF = keywordsDF[keywordsDF['CONVERSION'] != "TBC"].reset_index(drop = True)
        return keywordsDF
