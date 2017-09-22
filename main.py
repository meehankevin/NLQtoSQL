from getKeywords import *
from arrangeKeywords import *
from convertPhrases import *
from constructSQL import *
from collections import Counter
import time
from tkinter import *
from tkinter import ttk

def compute():
    try:
        data = datasource.get()
        NLQ = NLQsource.get()
        start = time.time()

        phraseslist = []
        table = data.replace("data/", "").replace(".csv", "")

        obj1 = getKeywords(NLQ, data)
        q1a, headers, headersDF0 = obj1.getExactHeaders(NLQ)
        q1b, headersDF = obj1.getSimilarHeaders(q1a, headers, headersDF0, 0.96)
        q2a, valuesDF0, headerValues, values = obj1.getExactValues(" ".join(q1b))
        q2b, valuesDF = obj1.getSimilarValues(q2a, values, valuesDF0, 0.95)
        valuesDFtest = valuesDF['WORD'].tolist()

        for word, count in Counter(valuesDFtest).most_common():
            valuesDFtest2 = valuesDF.loc[valuesDF['WORD'] == word, 'VALUE']
            testVal = valuesDFtest2.tolist()[0]
            for key, value in headerValues.items():
                if isinstance(value[0], str):
                    values = [word.lower() for word in value]
                    if testVal in values:
                        k = key
                        if k is not None and len(valuesDFtest2) > int(len(headerValues.get(k)) * 0.5):
                            headersDF.loc[len(headersDF)] = [word, key, 1]
                            valuesDF = valuesDF[valuesDF['WORD'] != word]
                        elif k is not None and len(valuesDFtest2) <= int(len(headerValues.get(k)) * 0.5) and count > 10:
                            q1a = punct_tokenizer.tokenize(word.lower())
                            q1b, headersDF = obj1.getSimilarHeaders(q1a, headers, headersDF, 0.85)
                            valuesDF = valuesDF[valuesDF['WORD'] != word]
        # ------------

        phrases = obj1.removeSchemaWords(NLQ, headersDF, valuesDF)

        obj2 = arrangeKeywords(NLQ, headersDF, valuesDF, phrases)
        keywordsDF = obj2.combineKeywords(headersDF, valuesDF, phrases)
        keywordsDF = obj2.orderKeywords(NLQ, keywordsDF)

        obj3 = convertPhrases(keywordsDF, data)
        keywordsDF = obj3.getPhraseConversion(keywordsDF)
        keywordsDF = obj3.stripNonConverted(keywordsDF)

        obj4 = constructSQL(keywordsDF, headerValues, data)
        SQL, pos1 = obj4.getSELECT(keywordsDF, headerValues, table)
        SQL, pos2 = obj4.getWHERE(keywordsDF, headerValues, SQL, pos1)
        SQL, pos3 = obj4.getOrderBy(keywordsDF, headerValues, SQL, pos2)
        SQL = obj4.getLIMIT(SQL)
        SQL = obj4.cleanSQL(SQL)
        for i, word in enumerate(SQL):
            if "(_)" in word:
                SQL[i] = word.replace("_", SQL[i+1])
                del SQL[i+1]
        SQL = " ".join(SQL)
        end = time.time()
        convertedSQL.set(SQL)
        timeTaken.set(end-start)
    except ValueError:
        pass

root = Tk()
root.title("Convert NLQ to SQL")

mainframe = ttk.Frame(root, padding="3 3 12 12")
mainframe.grid(column=0, row=0)
mainframe.columnconfigure(0, weight=1)
mainframe.rowconfigure(0, weight=1)

datasource = StringVar()
NLQsource = StringVar()
convertedSQL = StringVar()
timeTaken = StringVar()

ttk.Label(mainframe, text="Please insert NLQ:").grid(column=0, row=0)
NLQ_entry = ttk.Entry(mainframe, textvariable=NLQsource, width=50)
NLQ_entry.grid(column=1, row=0, sticky=(W, E))

ttk.Label(mainframe, text="Please insert path/to/datafile/csv:").grid(column=0, row=1)
NLQ_entry = ttk.Entry(mainframe, textvariable=datasource)
NLQ_entry.grid(column=1, row=1, sticky=(W, E))

ttk.Button(mainframe, text="Convert", command=compute).grid(row=2, columnspan=2)

ttk.Label(mainframe, text="SQL:").grid(column=0, row=3)
SQL_entry = ttk.Entry(mainframe, textvariable=convertedSQL)
SQL_entry.grid(column=1, row=3, sticky=(W, E))

ttk.Label(mainframe, text="Time (in milliseconds):").grid(column=0, row=4)
time_entry = ttk.Entry(mainframe, textvariable=timeTaken)
time_entry.grid(column=1, row=4, sticky=(W, E))

for child in mainframe.winfo_children(): child.grid_configure(padx=5, pady=5)

NLQ_entry.focus()
root.bind('<Return>', compute)

root.mainloop()