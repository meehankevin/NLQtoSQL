from nltk.corpus import stopwords
from nltk.corpus import wordnet as wn
from nltk.tokenize import word_tokenize
from nltk.tokenize import RegexpTokenizer as regx
from nltk.tokenize import MWETokenizer as mwet
from math import isnan
import pandas as pd
import numpy as np

punct_tokenizer = regx(r'\w+')

# Import stopwords
stop_words = set(stopwords.words("english"))

class getKeywords():

    def __init__(self, query = None, database = None):
        self.query = query
        self.database = database


    def removeStopwords(self, query = None):
        # ---------------------------
        # Module to remove stopwords from query
        # ---------------------------

        if query is None:
            query = self.query

        # remove punctuation
        words_no_punct = punct_tokenizer.tokenize(query.lower())
        res = []

        for w in words_no_punct:
            if w not in stop_words:
                res1 = res.append(w)

        return res

    def getExactHeaders(self, query):
        # -----------------------------------------------------------------
        # 1. Check query for exact match with headers
        #       If found append to res and remove from query for part 2
        # -----------------------------------------------------------------

        headersDF = pd.DataFrame(columns=['WORD', 'HEADER', 'SIMILARITY'])

        data = pd.read_csv(self.database, quotechar='"', skipinitialspace=True, encoding='latin1')
        headers = list(data)

        headers = [word.lower().replace("_", " ") for word in headers]
        headers1 = [punct_tokenizer.tokenize(word) for word in headers]

        tokenizer = mwet([phrase for phrase in headers1])

        q1a = tokenizer.tokenize(punct_tokenizer.tokenize(query.lower()))
        for phrase in q1a:
            used = False
            if phrase.replace("_", " ") in headers:
                headersDF.loc[len(headersDF)] = [phrase.replace("_", " "), phrase, 1]
                if phrase not in stop_words:
                    tmp = q1a.remove(phrase)
                used = True
            else:
                words = " ".join(headers)
                words = words.split()
                if phrase in words:
                    headersDF.loc[len(headersDF)] = [phrase.replace("_", " "), phrase, 1]
                    if phrase not in stop_words:
                        tmp = q1a.remove(phrase)
                    used = True

            if used == False:
                headers2 = [" ".join(word) for word in headers1]
                if phrase.replace("_", " ") in headers2:
                    headersDF.loc[len(headersDF)] = [phrase.replace("_", " "), phrase, 1]
                    if phrase not in stop_words:
                        tmp = q1a.remove(phrase)
                    used = True

        return q1a, headers, headersDF


    def getSimilarHeaders(self, q1a, headers, headersDF0, threshold):
        # -------------------------------------------------------------------------
        # Module to append dataframe of words and corresponding headers in database
        # -------------------------------------------------------------------------


        headersDF = headersDF0

        # -----------------------------------------------------------------
        # 2. Check remaining query for similar match with headers
        #       If found append to res
        # -----------------------------------------------------------------

        for w1 in q1a:
            for w in headers:
                # tokenize to deal with headers of more than one word
                w2 = word_tokenize(w)

                syns1 = wn.synsets(w1)

                for i in range(len(syns1)):  # i.e. for each word in query
                    word1 = wn.synset(syns1[i].name())
                    for j in range(len(w2)):  # i.e. for each header
                        syns2 = wn.synsets(w2[j])
                        for k in range(len(syns2)):  # i.e. for each word in each header
                            word2 = wn.synset(syns2[k].name())

                            sim = word1.wup_similarity(word2)

                            if not sim is None:
                                if sim > threshold:
                                    headersDF.loc[len(headersDF)] = [w1, w, sim]

        # Group and sort header_results by Similarity
        if headersDF.shape[0] > 1:
            headersDF = headersDF.groupby(['WORD', 'HEADER'], as_index=False, )['SIMILARITY'].max()
            headersDF = headersDF.sort_values('SIMILARITY', ascending=False)

            # remove stopwords
            headersDF = headersDF.loc[~headersDF['WORD'].isin(stop_words)]

            # remove words directly linked to headers from query
            q1b = [word for word in q1a if word not in headersDF['WORD'].tolist()]
        else:
            q1b = q1a

        headersDF = headersDF.reset_index(drop = True)

        return q1b, headersDF


    def getExactValues(self, query):
        # -----------------------------------------------------------------
        # 1. Check query for exact match with values
        #       If found append to res and remove from query for part 2
        # -----------------------------------------------------------------

        valuesDF = pd.DataFrame(columns=['WORD', 'VALUE', 'SIMILARITY'])

        data = pd.read_csv(self.database, quotechar='"', skipinitialspace=True, encoding='latin1')

        for col in data.select_dtypes(include = [np.number]):
            data[col] = data[col].fillna(0)
        for col in data.select_dtypes(exclude = [np.number]):
            data[col] = data[col].fillna("NULL")

        headerValues = {col: list(set(data[col].tolist())) for col in data.select_dtypes(exclude=[np.number])}
        values0 = []

        tmp = [values0.extend(word) for word in headerValues.values()] # clean list of values
        values = []
        tmp = [values.append(str(word).lower().replace("_", " ")) for word in values0]

        values1 = [punct_tokenizer.tokenize(word) for word in values] # tokenize each value string

        tokenizer = mwet([phrase for phrase in values1]) # create mwe for each value

        q2a = tokenizer.tokenize(punct_tokenizer.tokenize(query.lower())) # tokenize query on mwe

        for phrase in q2a:
            if phrase.replace("_", " ") in values:
                valuesDF.loc[len(valuesDF)] = [phrase.replace("_", " "), phrase.replace("_", " "), 1]
                tmp = q2a.remove(phrase)

        return q2a, valuesDF, headerValues, values


    def getSimilarValues(self, q2a, values, valuesDF0, threshold):
        # ------------------------------------------------------------------------
        # Module to create dataframe of words and corresponding values in database
        # ------------------------------------------------------------------------

        valuesDF = valuesDF0

        # -----------------------------------------------------------------
        # Check query for similar match with values
        #       If found append to res
        # -----------------------------------------------------------------

        for w1 in q2a:
            for w in values:
                # tokenize to deal with values of more than one word
                w2 = word_tokenize(str(w))
                syns1 = wn.synsets(w1)

                for i in range(len(syns1)):  # i.e. for each word in query
                    word1 = wn.synset(syns1[i].name())
                    for j in range(len(w2)):  # i.e. for each value
                        syns2 = wn.synsets(w2[j])
                        for k in range(len(syns2)):  # i.e. for each word in each value
                            word2 = wn.synset(syns2[k].name())

                            sim = word1.wup_similarity(word2)

                            if not sim is None:
                                if sim > threshold:
                                    valuesDF.loc[len(valuesDF)] = [w1, w, sim]


        if valuesDF.shape[0] > 1:
            # Group and sort value_results by Similarity
            valuesDF= valuesDF.groupby(['WORD', 'VALUE'], as_index=False, )['SIMILARITY'].max()
            valuesDF= valuesDF.sort_values('SIMILARITY', ascending=False)

            # remove words directly linked to values from query
            q2b = [word for word in q2a if word not in valuesDF['WORD'].tolist()]
        else:
            q2b = q2a

        # remove stopwords
        valuesDF = valuesDF.loc[~valuesDF['WORD'].isin(stop_words)]

        return q2b, valuesDF


    def removeSchemaWords(self, query, headers, values):
        # ---------------------------------------------------------------------------
        # Module to compute list of phrases not directly linked to headers or values
        # Note: accept query with stopwords as argument to split up concatenated phrases
        # --------------------------------------------------------------------------

        # query to be a list of each original word in the query
        # query1 to be query with headers/values concatenated

        query = query.replace(",", " in ") # hack to split words separated by punctuation: 'in' will be removed later by stopwords
        query1 = punct_tokenizer.tokenize(query.lower()) # remove punctuation & convert to lowercase
        query1 = " ".join(query1) # convert back to string

        tokens1 = [punct_tokenizer.tokenize(row) for row in headers['WORD'].tolist()]
        tokenizer1 = mwet([phrase for phrase in tokens1])  # create tokenizer for each header

        query1 = tokenizer1.tokenize(query1.split()) # tokenize query on headers
        query1 = " ".join(query1)  # convert back to a string

        tokens2 = [punct_tokenizer.tokenize(row) for row in values['WORD'].tolist()]
        tokenizer2 = mwet([phrase for phrase in tokens2])  # create tokenizer for each value

        query1 = tokenizer2.tokenize(query1.split())  # tokenize query on values
        query1 = [word.replace("_"," ") for word in query1]

        true = []  # binary vector: 1 denotes words linked to header/value/stopword, 0 denotes words not linked
        phrases = []  # vector of phrases
        data = []  # vector of headers and values

        for w in headers['WORD']:
            tmp = data.append(w)

        for w in values['WORD']:
            tmp = data.append(w)

        for w in stop_words:
            tmp = data.append(w)

        data = list(np.unique(data))

        for w in query1:
            if w in data:
                tmp = true.append(1)
            else:
                tmp = true.append(0)

        i = 0

        if true[i] == 0:
            substr = query1[i]
        else:
            substr = ""

        while i < len(true) - 1:
            if i == len(true) - 2 and true[i + 1] == 0:
                seq = (substr, query1[i + 1])
                substr = " ".join(seq)
                tmp = phrases.append(substr)
                i += 1
            elif true[i + 1] == 0:
                seq = (substr, query1[i + 1])
                substr = " ".join(seq)
                i += 1
            else:
                tmp = phrases.append(substr)
                substr = ""
                i += 1

        phrases[:] = [item for item in phrases if item] # removes empty elements
        return phrases
