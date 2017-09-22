import pandas as pd
from nltk.tokenize import MWETokenizer as mwet
from nltk.tokenize import RegexpTokenizer as regx

punct_tokenizer = regx(r'\w+')

class arrangeKeywords():

    def __init__(self, query, headers, values, phrases):
        self.query = query
        self.headers = headers
        self.values = values
        self.phrases = phrases

    def combineKeywords(self, headers, values, phrases):
        # set up dataframe of all keywords
        keywordsDF = pd.DataFrame(columns=['KEYWORD', 'TYPE', 'CONVERSION', 'POSITION'])

        for i, row in headers.iterrows():
            keywordsDF.loc[len(keywordsDF)] = [row['WORD'], 'HEADER', row['HEADER'], len(keywordsDF)]

        for i, row in values.iterrows():
            keywordsDF.loc[len(keywordsDF)] = [row['WORD'], 'VALUE', row['VALUE'], len(keywordsDF)]

        for phrase in phrases:
            keywordsDF.loc[len(keywordsDF)] = [phrase.strip(), 'FCN0', 'TBC', len(keywordsDF)]

        return keywordsDF

    def orderKeywords(self, query, keywordsDF):
        # tokenize query based on keywordsDF['KEYWORD'] and order

        #quick hack to remove duplicates
        # will have to revamp later
        #**************************************************************************
        keywordsDF = keywordsDF.groupby('KEYWORD', as_index = False).first()
        # **************************************************************************

        tmp = [punct_tokenizer.tokenize(word) for word in keywordsDF['KEYWORD'].tolist()]
        tokenizer = mwet([phrase for phrase in tmp])

        query = tokenizer.tokenize(punct_tokenizer.tokenize(query.lower()))
        query = [phrase.replace("_", " ") for phrase in query]

        i = 1
        for keyword in query:
            if keyword in keywordsDF['KEYWORD'].tolist():
                keywordsDF.loc[keywordsDF['KEYWORD'] == keyword, 'POSITION'] = i
                i += 1

        keywordsDF = keywordsDF.sort_values('POSITION')
        keywordsDF = keywordsDF.reset_index(drop = True)
        keywordsDF = keywordsDF.drop('POSITION', 1)
        return keywordsDF