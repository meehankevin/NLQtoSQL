# NLQtoSQL

This project was undertaken as part of my practicum for my MSc. in Computing (Software Engineering) in DCU. The goal was to implement a system capable of converting a Natural Language Query (i.e. a plain English query) related to some database into an SQL query. 
This repository contains a directory ("data") of some databases I looked at, my code and my final paper.

## Implementation
To implement the code, clone this repository and run the main class (I used PyCharm as my IDE), where you will be prompted to enter a Natural Language Query and the database which you are working on (the default being cwurData.csv). Compute to return the corresponding SQL and the time taken. Note that this system is neither entirely accurate nor optimized. Feel free to develop or to use the code for your own databases!

## Description of Classes

### 1. getKeywords.py
A module which analyses the NLQ for words deemed important relative to both the database and SQL in general

### 2. arrangeKeywords.py
A module which sorts the keywords based on their order in the NLQ

### 3. convertPhrases.py
A module which converts words/groups of words related to SQL functions

### 4. constructSQL.py
A module which forms the SQL query based on predefined patterns

### 5. main.py 
A module which brings up an interface for converting a user's NLQ to SQL
