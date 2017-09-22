from nltk.corpus import stopwords
from nltk.corpus import wordnet as wn
from nltk.tokenize import word_tokenize
from nltk.tokenize import RegexpTokenizer as regx
from nltk.tokenize import MWETokenizer as mwet
import pandas as pd
import numpy as np
import re
from six import string_types

class constructSQL():

    def __init__(self, keywordsDF, headersValues, table):
        self.keywordsDF = keywordsDF
        self.headersValues = headersValues
        self.table = table

    def getSELECT(self, keywordsDF, headersValues, table):
        # start the query
        # all queries should begin with a select
        SQL = []
        condition_by_value = False
        pos = 0
        n = keywordsDF.shape[0] - 1  # note final row not included but should not be header anyway
        for i, row in keywordsDF.iterrows():
            if 'SELECT' in row['CONVERSION'].split():
                keywordsDF = keywordsDF.set_value(i, 'TYPE', "FCN1") #this isn't working but not sure why
                tmp = SQL.append(row['CONVERSION'])
                j = i + 1
                if j == n - 1:  # pos is second last row
                    k = -1
                else:
                    k = j + 1
                if keywordsDF.iloc[j][1] == 'FCN0' and keywordsDF.iloc[k][1] == 'HEADER':
                    tmp = SQL.extend([keywordsDF.loc[j][2], keywordsDF.iloc[k][2]])
                    j += 2
                elif keywordsDF.iloc[j][1] == 'VALUE':
                    if j == keywordsDF.shape[0] - 1:
                        for key, values in headersValues.items():
                            values1 = [word.lower() for word in values]
                            for i, x in enumerate(values1):
                                if j < keywordsDF.shape[0] and x == keywordsDF.iloc[j][2]:
                                    tmp = SQL.append(key)
                                    condition_by_value = True
                                    k = key
                                    v = values[i]
                                    j += 1
                    else:
                        SQL = 'SYNTAX NOT VALID: HEADER/FUNCTION/ADJECTIVE READ AS VALUE'

                while j < n and keywordsDF.iloc[j][1] == 'HEADER':
                    tmp = SQL.append(keywordsDF.loc[j][2])
                    j += 1
                    if j < n and keywordsDF.iloc[j][1] == 'HEADER':
                        tmp = SQL.append(',')

                pos = j
                if not isinstance(SQL, str):
                    tmp = SQL.append("FROM")
                    tmp = SQL.append(table)
                    if condition_by_value == True:
                        tmp = SQL.extend(["WHERE", k, "=", v])
        return SQL, pos

    def getWHERE(self, keywordsDF, headersValues, SQL, pos):
        j = pos
        if j >= keywordsDF.shape[0]:
            return SQL, pos
        else:

            if not isinstance(SQL, str) and keywordsDF.iloc[j][1] == 'VALUE':

                keys = [word.lower() for word in headersValues.keys()]
                for key, values in headersValues.items():
                    values1 = [word.lower() for word in values]
                    for i, x in enumerate(values1):
                        if j < keywordsDF.shape[0] and x == keywordsDF.iloc[j][2] and key.lower() in keywordsDF['CONVERSION'].tolist():
                            if j + 1 == keywordsDF.shape[0]:
                                k = -1
                            else:
                                k = j + 1
                            if keywordsDF.iloc[k][2] in keys:
                                tmp = SQL.extend(["WHERE", keywordsDF.iloc[k][2], "=", values[i]])
                            else:
                                tmp = SQL.extend(["WHERE", key, "=", values[i]])
                        elif j < keywordsDF.shape[0] and x == keywordsDF.iloc[j][2] and "WHERE" not in SQL:
                            if j + 1 == keywordsDF.shape[0]:
                                k = -1
                            else:
                                k = j + 1
                            if keywordsDF.iloc[k][2] in keys:
                                tmp = SQL.extend(["WHERE", keywordsDF.iloc[k][2], "=", values[i]])
                            else:
                                tmp = SQL.extend(["WHERE", key, "=", values[i]])
                            if j + 1 < keywordsDF.shape[0]:
                                j += 1




        if not isinstance(SQL, str):
            df = keywordsDF[keywordsDF['TYPE'] == 'DATE']
            countDates = len(df)
            if countDates == 1:
                tmp = SQL.extend(["WHERE", df.iloc[0][2], "=", df.iloc[0][0]])
            elif countDates == 2:
                df = df.sort_values('KEYWORD')
                tmp = SQL.extend(["WHERE", df.iloc[0][2], ">=", df.iloc[0][0], "AND", df.iloc[1][2], "<=", df.iloc[1][0]])
            elif countDates == 3:
                df = df.sort_values('KEYWORD')
                tmp = SQL.append("WHERE")
                for i, row in df.iterrows():
                    tmp = SQL.extend([row['CONVERSION'], "=", row['KEYWORD'], "OR"])
                del SQL[-1]

        return SQL, j

    def getOrderBy(self, keywordsDF, headersValues, SQL, pos):
        j = pos
        if j >= keywordsDF.shape[0]:
            return SQL, pos
        else:
            if keywordsDF.shape[0] - 1 - j == 0 or isinstance(SQL, str) or (SQL is None) or (keywordsDF.iloc[j][1] != 'FCN0' and  keywordsDF.iloc[j][1] != 'HEADER'):
                return SQL, pos
            else:
                if keywordsDF.shape[0] - j == 0: # pos is second last row
                    k = -1
                else:
                    k = j+1
                logical_operator = ""
                fcn = 0
                hdr = 0
                if (keywordsDF.iloc[j][1] == 'FCN0' and keywordsDF.iloc[k][1] == 'HEADER'):
                    fcn = j
                    hdr = k
                elif (keywordsDF.iloc[k][1] == 'FCN0' and keywordsDF.iloc[j][1] == 'HEADER'):
                    fcn = k
                    hdr = j

                if keywordsDF.iloc[hdr][2] not in headersValues.keys(): # if header is for numeric column
                    if re.search('(\s)(\d+)$' , keywordsDF.iloc[fcn][2]): # if number in FCN0 ****SHOULD BE FCN NOT J****
                        if 'MAX' in keywordsDF.iloc[fcn][2].split():
                            logical_operator = "<="
                        elif 'MIN' in keywordsDF.iloc[fcn][2].split():
                            logical_operator = ">="
                        tmp = SQL.extend(["AND", keywordsDF.iloc[hdr][2], logical_operator, keywordsDF.iloc[fcn][2].split()[-1]])
                    else:
                        if 'MAX' in keywordsDF.iloc[fcn][2].split():
                            tmp = SQL.extend(["ORDER BY", keywordsDF.iloc[hdr][2], "LIMIT 1"]) # i.e. from highest number down
                        elif 'MIN' in keywordsDF.iloc[fcn][2].split():
                            tmp = SQL.extend(["ORDER BY", keywordsDF.iloc[hdr][2], "DESC", "LIMIT 1"]) #i.e. from lowest up
        return SQL, pos

    def getLIMIT(self, SQL):
        if not isinstance(SQL, str):
            SQL = " ".join(SQL)
            SQL = SQL.split()
            count = 0;
            pos = []
            for i, phrase in enumerate(SQL):
                if 'LIMIT' in phrase:
                    count += 1
                    tmp = pos.append(i)

            if count == 1:
                tmp = SQL.extend([SQL[pos[0]], SQL[pos[0] + 1]])
                del SQL[pos[0]]
                del SQL[pos[0]]
            elif count > 1:
                tmp = SQL.extend([SQL[pos[0]], SQL[pos[0] + 1]])
                i = 0
                while i < count:
                    del SQL[pos[i]]
                    del SQL[pos[i]]
                    if i + 1 < count:
                        pos[i+1] = pos[i+1] - 1
                    i += 1

        return SQL

    def cleanSQL(self, SQL):
        # trim 'WHERE'
        countWHERE = 0
        pos = []
        for i, phrase in enumerate(SQL):
            if phrase == 'WHERE':
                countWHERE += 1
                tmp = pos.append(i)

        if countWHERE > 1:
            start = 1
            for j in range(start, len(pos)):
                k = pos[j]
                SQL[k] = 'AND'

        return SQL
